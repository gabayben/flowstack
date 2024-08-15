from copy import deepcopy
from enum import StrEnum
import logging
from typing import Any, Optional, Unpack

from pymilvus import AnnSearchRequest, Collection, DataType, MilvusClient, RRFRanker, WeightedRanker

from flowstack.artifacts import Artifact, TextLike, Text, artifact_registry
from flowstack.milvus import ScalarMetadataFilters
from flowstack.milvus.utils import (
    MilvusSparseEmbeddingFunction,
    get_default_sparse_embedding_function,
    to_milvus_filter
)
from flowstack.stores import VectorStore, VectorStoreQuery, VectorStoreQueryMode, VectorStoreQueryResult
from flowstack.typing import Embedding, FilterOperator, MetadataFilter, MetadataFilters
from flowstack.core.utils.constants import DEFAULT_DOC_ID_KEY, DEFAULT_EMBEDDING_KEY
from flowstack.core.utils.func import iter_batch

MILVUS_ID_FIELD = 'id'
DEFAULT_BATCH_SIZE = 100

logger = logging.getLogger(__name__)

class IndexManagement(StrEnum):
    NO_VALIDATION = 'no_validation'
    CREATE_IF_NOT_EXISTS = 'create_if_not_exists'

class MilvusVectorStore(VectorStore):
    _client: MilvusClient
    _collection: Collection

    @property
    def client(self) -> MilvusClient:
        return self._client

    @property
    def collection(self) -> Collection:
        return self._collection

    @property
    def _dense_index_params(self) -> dict:
        base_params = self.index_config.copy()
        index_type = base_params.pop('index_type', 'FLAT')
        return {
            'params': base_params,
            'index_type': index_type,
            'metric_type': self.similarity_metric
        }

    def __init__(
        self,
        uri: str = 'http://localhost:19530',
        token: str = '',
        collection_name: str = 'flowstack',
        dim: Optional[int] = None,
        embedding_field: str = DEFAULT_EMBEDDING_KEY,
        doc_id_field: str = DEFAULT_DOC_ID_KEY,
        text_key: Optional[str] = None,
        output_fields: list[str] = [],
        similarity_metric: str = 'IP',
        consistency_level: str = 'Strong',
        overwrite: bool = False,
        index_config: dict = {},
        search_config: dict = {},
        batch_size: int = DEFAULT_BATCH_SIZE,
        max_length: int = 65_535,
        sparse_embedding_field: str = 'sparse_embedding',
        sparse_embedding_function: Optional[MilvusSparseEmbeddingFunction] = None,
        enable_sparse: bool = False,
        hybrid_ranker: str = 'RRFRanker',
        hybrid_ranker_params: dict = {},
        index_management: IndexManagement = IndexManagement.CREATE_IF_NOT_EXISTS,
        collection_kwargs: dict = {},
        **client_kwargs
    ):
        self.uri = uri
        self.token = token
        self.collection_name = collection_name
        self.dim = dim
        self.embedding_field = embedding_field
        self.doc_id_field = doc_id_field
        self.text_key = text_key
        self.output_fields = output_fields
        self.similarity_metric = similarity_metric
        self.consistency_level = consistency_level
        self.overwrite = overwrite
        self.index_config = index_config
        self.search_config = search_config
        self.batch_size = batch_size
        self.max_length = max_length
        self.sparse_embedding_field = sparse_embedding_field
        self.sparse_embedding_function = sparse_embedding_function
        self.enable_sparse = enable_sparse
        self.hybrid_ranker = hybrid_ranker
        self.hybrid_ranker_params = hybrid_ranker_params
        self.index_management = index_management

        self._client = MilvusClient(uri=uri, token=token, **client_kwargs)
        if overwrite and collection_name in self._client.list_collections():
            self.client.drop_collection(collection_name)
        if collection_name not in self._client.list_collections():
            if dim is None:
                raise ValueError('dim argument required for collection creation.')
            if not self.enable_sparse:
                self.client.create_collection(
                    collection_name=collection_name,
                    dimension=dim,
                    primary_field_name=MILVUS_ID_FIELD,
                    vector_field_name=embedding_field,
                    id_type='string',
                    metric_type=similarity_metric,
                    consistency_level=consistency_level,
                    max_length=max_length,
                    **collection_kwargs
                )
            else:
                self._create_hybrid_index()

        self._collection = Collection(collection_name, using=self.client._using)
        self._create_index_if_required()

        if self.enable_sparse is True and sparse_embedding_function is None:
            logger.info("Sparse embedding function is not provided, using default.")
            self.sparse_embedding_function = get_default_sparse_embedding_function()
        elif self.enable_sparse is True and sparse_embedding_function is not None:
            self.sparse_embedding_function = sparse_embedding_function

        logger.debug(f"Successfully created a new collection: {self.collection_name}")

    def retrieve(
        self,
        mode: str = VectorStoreQueryMode.DEFAULT,
        query_value: Optional[TextLike] = None,
        query_embedding: Optional[Embedding] = None,
        ref_artifact_ids: Optional[list[str]] = None,
        artifact_ids: Optional[list[str]] = None,
        filters: Optional[MetadataFilters] = None,
        output_fields: Optional[list[str]] = None,
        similarity_top_k: Optional[int] = None,
        additional_kwargs: dict[str, Any] = {},
        **query: Unpack[VectorStoreQuery]
    ) -> VectorStoreQueryResult:
        if mode not in [VectorStoreQueryMode.DEFAULT, VectorStoreQueryMode.HYBRID]:
            raise ValueError(f'Query mode {mode} is not supported in Milvus.')
        if mode == VectorStoreQueryMode.HYBRID and not self.enable_sparse:
            raise ValueError('Query mode is hybrid, but enable_sparse is False.')
        if mode == VectorStoreQueryMode.HYBRID and query_value is None:
            raise ValueError('Query mode is hybrid, but query was not provided.')
        if query_embedding is None:
            raise ValueError(f'Query embedding is not set.')

        expressions = []
        output_fields = ['*']
        additional_kwargs = additional_kwargs or {}
        scalar_filters: Optional[ScalarMetadataFilters] = additional_kwargs.get('scalar_filters')

        # Parse the filter
        if filters is not None or scalar_filters is not None:
            expressions.append(to_milvus_filter(filters, scalar_filters))

        # Parse any ref artifacts we are filtering on
        if ref_artifact_ids is not None and len(ref_artifact_ids) != 0:
            expr_list = [f'"{artifact_id}"' for artifact_id in ref_artifact_ids]
            expressions.append(f'{self.doc_id_field} in [{','.join(expr_list)}]')

        # Parse any artifacts we are filtering on
        if artifact_ids is not None and len(artifact_ids) != 0:
            expr_list = [f'"{artifact_id}"' for artifact_id in artifact_ids]
            expressions.append(f'{MILVUS_ID_FIELD} in [{','.join(expr_list)}]')

        # Limit output fields
        outputs_limited = False
        if output_fields is not None:
            outputs_limited = True
        elif len(self.output_fields) > 0:
            output_fields = self.output_fields
            outputs_limited = True

        # Add the text key to output_fields if necessary
        if output_fields is not None and self.text_key not in output_fields and outputs_limited:
            output_fields.append(self.text_key)

        # Convert to string expression
        expression_str = ''
        if len(expressions) > 0:
            expression_str = ' and '.join(expressions)

        # Perform the search
        artifacts: list[Artifact] = []
        ids: list[str] = []
        similarities: list[float] = []
        if mode == VectorStoreQueryMode.DEFAULT:
            results = self.client.search(
                self.collection_name,
                data=[query_embedding.tolist()],
                filter=expression_str,
                output_fields=output_fields,
                limit=similarity_top_k,
                search_params=self.search_config,
                anns_field=self.embedding_field
            )[0]
            logger.debug(
                f'Successfully searched embedding in collection: {self.collection_name}.'
                f'Num results: {len(results)}.'
            )
            for result in results:
                entity = result.pop('entity') or {}
                artifact = artifact_registry.deserialize({**result, **entity})
                artifacts.append(artifact)
                ids.append(result['id'])
                similarities.append(result['distance'])
        else:
            dense_request = AnnSearchRequest(
                data=[query_embedding],
                anns_field=self.embedding_field,
                expr=expression_str,
                limit=similarity_top_k,
                param={
                    'metric_type': self.similarity_metric,
                    'params': self.search_config
                }
            )

            query_value = query_value if isinstance(query_value, Artifact) else Text(query_value) # type: ignore[call-args]
            sparse_embedding = self.sparse_embedding_function.encode_queries([query_value])[0]
            sparse_request = AnnSearchRequest(
                data=[sparse_embedding],
                anns_field=self.sparse_embedding_field,
                expr=expression_str,
                limit=similarity_top_k,
                param={'metric_type': 'IP'}
            )

            ranker = None
            if self.hybrid_ranker == 'RRFRanker':
                if not self.hybrid_ranker_params:
                    self.hybrid_ranker_params = {'k': 60}
                ranker = RRFRanker(**self.hybrid_ranker_params)
            elif self.hybrid_ranker == 'WeightedRanker':
                if not self.hybrid_ranker_params:
                    self.hybrid_ranker_params = {'weights': [1., 1.]}
                ranker = WeightedRanker(self.hybrid_ranker_params['weights'])
            else:
                raise ValueError(f'Unsupported ranker: {self.hybrid_ranker}.')

            results = self.collection.hybrid_search(
                [dense_request, sparse_request],
                rerank=ranker,
                limit=similarity_top_k,
                output_fields=output_fields
            )[0]
            for result in results:
                entity = result.pop('entity') or {}
                artifact = artifact_registry.deserialize({**result, **entity})
                artifacts.append(artifact)
                ids.append(result.id)
                similarities.append(result.distance)

        return VectorStoreQueryResult(
            artifacts=artifacts,
            ids=ids,
            similarities=similarities
        )

    def insert(
        self,
        artifacts: list[Artifact],
        force_flush: bool = False,
        **kwargs
    ) -> list[str]:
        insert_ids = []
        insert_entries = []

        for artifact in artifacts:
            entry = artifact.store_model_dump()
            entry[MILVUS_ID_FIELD] = artifact.id
            entry[self.embedding_field] = artifact.embedding
            if self.enable_sparse:
                entry[self.sparse_embedding_field] = self.sparse_embedding_function.encode_documents([artifact])[0]
            insert_ids.append(artifact.id)
            insert_entries.append(entry)

        for batch in iter_batch(insert_entries, self.batch_size):
            self.collection.insert(batch, **kwargs)
        if force_flush:
            self.collection.flush()
        self._create_index_if_required()

        logger.debug(
            f'Successfully inserted embeddings into {self.collection_name}. '
            f'Num inserted: {len(insert_entries)}.'
        )
        return insert_ids

    def delete(
        self,
        artifact_ids: Optional[list[str]] = None,
        filters: Optional[MetadataFilters] = None,
        scalar_filters: Optional[ScalarMetadataFilters] = None,
        **kwargs
    ) -> None:
        filters_copy = deepcopy(filters) or MetadataFilters(filters=[])
        if artifact_ids:
            filters_copy.append(MetadataFilter(
                MILVUS_ID_FIELD,
                artifact_ids,
                operator=FilterOperator.IN
            ))
        filter = (
            to_milvus_filter(filters_copy, scalar_filters=scalar_filters)
            if filters is not None
            else None
        )
        self.client.delete(self.collection_name, filter=filter, **kwargs)
        logger.debug('Successfully deleted artifacts.')

    def delete_refs(self, ref_ids: list[str], **kwargs) -> None:
        ref_ids = [f'"{ref_id}"' for ref_id in ref_ids]
        entries = self.client.query(
            self.collection_name,
            filter=f'{self.doc_id_field} in [{','.join(ref_ids)}]'
        )
        if len(entries) > 0:
            ids = [entry['id'] for entry in entries]
            self.client.delete(self.collection_name, ids=ids)
            logger.debug(f'Successfully deleted artifacts: {ids}')

    def clear(self, **kwargs) -> None:
        self._client.drop_collection(self.collection_name, **kwargs)

    def _create_index_if_required(self) -> None:
        if self.index_management == IndexManagement.NO_VALIDATION:
            return
        if not self.enable_sparse:
            self._create_dense_index()
        else:
            self._create_hybrid_index()

    def _create_dense_index(self) -> None:
        index_exists = self.collection.has_index()
        if (
            (not index_exists and self.index_management == IndexManagement.CREATE_IF_NOT_EXISTS) or
            (index_exists and self.overwrite)
        ):
            if index_exists:
                self.collection.release()
                self.collection.drop_index()
            self.collection.create_index(self.embedding_field, index_params=self._dense_index_params)
            self.collection.load()

    def _create_hybrid_index(self) -> None:
        if self.collection_name not in self._client.list_collections():
            schema = MilvusClient.create_schema(auto_id=False, enable_dynamic_field=True)
            schema.add_field(
                MILVUS_ID_FIELD,
                datatype=DataType.VARCHAR,
                max_length=self.max_length,
                is_primary=True
            )
            schema.add_field(
                self.embedding_field,
                datatype=DataType.FLOAT_VECTOR,
                dim=self.dim
            )
            schema.add_field(
                self.sparse_embedding_field,
                datatype=DataType.SPARSE_FLOAT_VECTOR
            )
            self.client.create_collection(self.collection_name, schema=schema)
        self._collection = Collection(self.collection_name, self.client._using)

        dense_index_exists = self.collection.has_index(index_name=self.embedding_field) # type: ignore[call-args]
        sparse_index_exists = self.collection.has_index(index_name=self.sparse_embedding_field) # type: ignore[call-args]

        if (
            (
                (not dense_index_exists or not sparse_index_exists) and
                self.index_management == IndexManagement.CREATE_IF_NOT_EXISTS
            ) or (dense_index_exists and sparse_index_exists and self.overwrite)
        ):
            if dense_index_exists:
                self.collection.release()
                self.collection.drop_index(index_name=self.embedding_field) # type: ignore[call-args]
            if sparse_index_exists:
                self.collection.drop_index(index_name=self.sparse_embedding_field) # type: ignore[call-args]
            self.collection.create_index(self.embedding_field, index_params=self._dense_index_params)
            self.collection.create_index(
                self.sparse_embedding_field,
                index_params={
                    'index_type': 'SPARSE_INVERTED_INDEX',
                    'metric_type': 'IP'
                }
            )

        self.collection.load()