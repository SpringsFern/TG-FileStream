# TG-FileStream
# Copyright (C) 2025 Deekshith SH

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

import importlib.util
import logging

from pathlib import Path
from telethon import TelegramClient, functions

from tgfs.config import Config

log = logging.getLogger(__name__)

client = TelegramClient(
    "tg-filestream",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    receive_updates=not Config.NO_UPDATE
)

def load_plugins(folder_path: str) -> None:
    folder = Path(folder_path)
    package_prefix = ".".join(folder.parts)
    for file in folder.glob("*.py"):
        module_name = f"{package_prefix}.{file.stem}"
        spec = importlib.util.spec_from_file_location(module_name, str(file))
        module = importlib.util.module_from_spec(spec)
        module.__package__ = package_prefix
        spec.loader.exec_module(module)
        log.info("Imported %s", module_name)
