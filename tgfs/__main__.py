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
import logging
import traceback
from aiohttp import web
from telethon import functions
from telethon.tl.types import User, Config

from tgfs.log import log
from tgfs.config import Config
from tgfs.paralleltransfer import ParallelTransferrer
from tgfs.telegram import client, load_plugins, multi_clients, start_clients
from tgfs.routes import routes
from tgfs.database import DB
from tgfs.utils import load_configs
load_plugins('tgfs/patches')

app = web.Application()
app.add_routes(routes)
runner = web.AppRunner(app)

async def start() -> None:
    await DB.init()
    await load_configs()
    await client.start(bot_token=Config.BOT_TOKEN)
    if not Config.NO_UPDATE:
        load_plugins("tgfs/plugins")

    # https://github.com/LonamiWebs/Telethon/blob/59da66e105ba29eee7760538409181859c7d310d/telethon/client/downloads.py#L62
    config = await client(functions.help.GetConfigRequest())
    for option in config.dc_options:
        if option.ip_address == client.session.server_address:
            client.session.set_dc(
                option.id, option.ip_address, option.port)
            client.session.save()
            break
    me: User = await client.get_me()
    transfer = ParallelTransferrer(client, me.id)
    transfer.post_init()
    multi_clients.append(transfer)
    await start_clients()
    await runner.setup()
    await web.TCPSite(runner, Config.HOST, Config.PORT).start()
    log.info("Username: %s", me.username)
    log.info("DC ID: %d", getattr(client.session, "dc_id", None))
    log.info("URL: %s", Config.PUBLIC_URL)


async def stop() -> None:
    log.debug("Stopping HTTP Server")
    await runner.cleanup()
    log.debug("Closing Telegram Client and Connections")
    await client.disconnect()
    log.debug("Closing Database Connection")
    await DB.close()
    log.info("Stopped Bot and Server")

async def main() -> None:
    try:
        await start()
        await client.run_until_disconnected()
    finally:
        await stop()
        logging.info("Stopped Services")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception:
        logging.error(traceback.format_exc())
