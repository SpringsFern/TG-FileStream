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

import logging
from tgfs.config import Config

LOG_LEVEL = logging.DEBUG if Config.DEBUG else logging.INFO
EXT_LOG_LEVEL = logging.INFO if Config.EXT_DEBUG else logging.ERROR
logging.basicConfig(level=LOG_LEVEL)
logging.getLogger("telethon").setLevel(EXT_LOG_LEVEL)
logging.getLogger("aiohttp").setLevel(EXT_LOG_LEVEL)
logging.getLogger("asyncio").setLevel(EXT_LOG_LEVEL)
logging.getLogger("pymongo").setLevel(EXT_LOG_LEVEL)
log = logging.getLogger("tgstream")
