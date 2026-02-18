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

import sys
import base64
import hashlib
import hmac
import struct
import time
import importlib.util
from typing import Optional, cast
from pathlib import Path

from telethon import Button
from telethon.utils import get_input_location
from telethon.tl.custom import Message

from tgfs.config import Config
from tgfs.paralleltransfer import ParallelTransferrer
from tgfs.utils.types import FileSource, InputTypeLocation, User
from tgfs.telegram import client
from tgfs.database import DB

START_TIME = time.monotonic()

async def update_location(source: FileSource, transfer: ParallelTransferrer) -> InputTypeLocation:
    message = cast(Message, await client.forward_messages(Config.BIN_CHANNEL, source.message_id, source.chat_id, drop_author=True))
    msg = cast(Message, await transfer.client.get_messages(message.chat_id, ids=message.id))
    await message.delete()
    _, location = get_input_location(msg)
    await DB.db.upsert_location(transfer.client_id, location)
    return location

async def check_get_user(user_id: int, msg_id, required: bool = True) -> Optional[User]:
    if Config.ALLOWED_IDS and user_id not in Config.ALLOWED_IDS:
        return None
    user = await DB.db.get_user(user_id)
    if required and user is None:
        await client.send_message(
            user_id, "Please agree to the Terms of Service before using the bot.",
            buttons=[[Button.inline('Agree', f'tos_agree_{msg_id}'.encode('utf-8'))]]
        )
    if user is not None and user.is_banned:
        await client.send_message(user_id, "You are banned from using this bot.")
        return None
    return user

async def load_configs():
    Config.SECRET = await DB.db.get_secret()

def base64_encode(data: bytes) -> str:
    encoded = base64.urlsafe_b64encode(data)
    return encoded.decode('ascii').rstrip("=")

def base64_decode(string: str) -> bytes:
    padding = 4 - (len(string) % 4)
    string = string + ("=" * padding)
    return base64.urlsafe_b64decode(string)

def make_token(user_id: int, file_id: int) -> str:
    payload = struct.pack(">QQ", user_id, file_id)
    sig = hmac.new(Config.SECRET, payload, hashlib.sha256).digest()

    token = (
        base64_encode(payload)
        + "/"
        + base64_encode(sig)
    )
    return token

def parse_token(p_b64: str, s_b64: Optional[str] = None) -> tuple[int, int] | None:
    try:
        payload = base64_decode(p_b64)
        sig = base64_decode(s_b64)

        if s_b64 is not None:
            expected = hmac.new(Config.SECRET, payload, hashlib.sha256).digest()
            if not hmac.compare_digest(sig, expected):
                return None

        user_id, file_id = struct.unpack(">QQ", payload)
        return user_id, file_id
    except Exception:
        return None

def human_time(seconds: int):
    mins, sec = divmod(seconds, 60)
    hrs, mins = divmod(mins, 60)
    days, hrs = divmod(hrs, 24)
    return f"{days}d {hrs}h {mins}m {sec}s"

def uptime_human():
    return human_time(int(time.monotonic() - START_TIME))

def human_bytes(size: int) -> str:
    if size == 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB", "PB", "EB"]
    i = 0
    while size >= 1024 and i < len(units) - 1:
        size /= 1024
        i += 1
    return f"{size:.2f} {units[i]}"

def load_patches(patches_path: str):
    patches_path = Path(patches_path).resolve()

    loaded_files = set()

    for item in patches_path.iterdir():
        if item.is_file() and item.suffix == ".py":
            load_file(item, patches_path, loaded_files)

        elif item.is_dir():

            init_file = item / "__init__.py"

            if init_file.exists():
                load_file(init_file, patches_path, loaded_files)

            else:
                for file in item.rglob("*.py"):
                    load_file(file, patches_path, loaded_files)


def load_file(file: Path, base: Path, loaded: set):
    if file in loaded:
        return

    module_name = "patches_" + "_".join(
        file.relative_to(base).with_suffix("").parts
    )

    spec = importlib.util.spec_from_file_location(module_name, file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    loaded.add(file)
