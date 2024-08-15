# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
# SPDX-License-Identifier: Apache-2.0

from abc import ABC, abstractmethod
from enum import StrEnum
import os
from typing import Any, Optional, Union

class SecretType(StrEnum):
    TOKEN = 'token'
    ENV_VAR = 'env_var'

class Secret(ABC):
    @property
    @abstractmethod
    def secret_type(self) -> str:
        pass

    @classmethod
    def from_token(cls, token: str) -> 'Secret':
        return TokenSecret(token)

    @classmethod
    def from_env_var(
        cls,
        env_vars: Union[str, tuple[str, ...]],
        strict: bool = False
    ) -> 'Secret':
        return EnvVarSecret(env_vars, strict=strict)

    @abstractmethod
    def resolve_value(self) -> Optional[Any]:
        """
        Resolve the secret to an atomic value. The semantics of the value is secret-dependent.

        :returns:
            The value of the secret, if any.
        """

class TokenSecret(Secret):
    @property
    def secret_type(self) -> str:
        return SecretType.TOKEN

    def __init__(self, token: str):
        self._token = token

    def resolve_value(self) -> Optional[Any]:
        return self._token

class EnvVarSecret(Secret):
    _env_vars: tuple[str, ...]

    @property
    def secret_type(self) -> str:
        return SecretType.ENV_VAR

    def __init__(
        self,
        env_vars: Union[str, tuple[str, ...]],
        strict: bool = False
    ):
        self._env_vars = (env_vars,) if isinstance(env_vars, str) else env_vars
        self._strict = strict

    def resolve_value(self) -> Optional[Any]:
        out = None
        for env_var in self._env_vars:
            value = os.getenv(env_var)
            if value is not None:
                out = value
                break
        if out is None and self._strict:
            raise ValueError(f'None of the following environment variables are set: {self._env_vars}.')
        return out