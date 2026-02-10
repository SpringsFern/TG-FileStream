# TG-FileStream
# Copyright (C) 2025-2026 Deekshith SH

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from __future__ import annotations

from os import environ
from typing import Any

class ConfigBase:
    @staticmethod
    def env_bool(key: str, default: bool = False) -> bool:
        val = environ.get(key)
        if val is None:
            return default
        return val.lower() in ("1", "true", "yes", "on")

    @staticmethod
    def env_int(key: str, default: int) -> int:
        return int(environ.get(key, default))

    @staticmethod
    def get_multi_client_tokens() -> list[str]:
        prefix = "MULTI_TOKEN"
        tokens: list[tuple[int, str]] = []

        for key, value in environ.items():
            if key.startswith(prefix):
                suffix = key[len(prefix):]
                if suffix.isdigit():
                    tokens.append((int(suffix), value))

        tokens.sort(key=lambda x: x[0])
        return [token for _, token in tokens]

    @staticmethod
    def load_backend_config(
        prefix: str,
        schema: dict[str, tuple[type, Any]],
        required: set[str],
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = {}
        missing: list[str] = []

        for key, (typ, default) in schema.items():
            env_key = f"{prefix}_{key.upper()}"

            if env_key in environ:
                kwargs[key] = typ(environ[env_key])
            elif default is not None:
                kwargs[key] = default
            else:
                missing.append(env_key)

        if set(missing) & required:
            raise RuntimeError(
                f"Missing required environment variables: {', '.join(missing)}"
            )

        return kwargs
