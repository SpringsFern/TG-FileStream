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

import asyncio
import importlib.util
import logging

from pathlib import Path
import sys
from typing import Optional
from telethon import TelegramClient, functions
from telethon.sessions import MemorySession
from telethon.tl.types import InputPeerUser

from tgfs.config import Config
from tgfs.paralleltransfer import ParallelTransferrer

log = logging.getLogger(__name__)

multi_clients: list[ParallelTransferrer] = []

client = TelegramClient(
    "tg-filestream",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    receive_updates=not Config.NO_UPDATE,
    sequential_updates=Config.SEQUENTIAL_UPDATES
)

async def _start_client(token: str) -> Optional[ParallelTransferrer]:
    bot = TelegramClient(
        MemorySession(),
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        receive_updates=False
    )
    try:
        await bot.start(bot_token=token)
        # https://github.com/LonamiWebs/Telethon/blob/59da66e105ba29eee7760538409181859c7d310d/telethon/client/downloads.py#L62
        config = await bot(functions.help.GetConfigRequest())
        for option in config.dc_options:
            if option.ip_address == bot.session.server_address:
                bot.session.set_dc(
                    option.id, option.ip_address, option.port)
                bot.session.save()
                break
        me: InputPeerUser = await bot.get_me(True)
        transfer = ParallelTransferrer(bot, me.user_id)
        transfer.post_init()
        return transfer
    except Exception as e:
        log.error("Faied to Start Client %s: %s", token.split(":")[0], e)
        return None
    
async def start_clients():
    tasks = (_start_client(t) for t in Config.TOKENS)
    results = await asyncio.gather(*tasks)
    multi_clients.extend(filter(None, results))

def load_plugins(folder_path: str) -> None:
    folder = Path(folder_path)
    package_prefix = ".".join(folder.parts)
    for file in folder.glob("*.py"):
        module_name = f"{package_prefix}.{file.stem}"
        if module_name in sys.modules:
            log.debug("Already Imported %s, skipping", module_name)
            continue
        spec = importlib.util.spec_from_file_location(module_name, str(file))
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        module.__package__ = package_prefix
        spec.loader.exec_module(module)
        log.info("Imported %s", module_name)
