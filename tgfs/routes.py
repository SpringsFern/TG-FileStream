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
import asyncio
from aiohttp import web

from tgfs.paralleltransfer import ParallelTransferrer
from tgfs.utils import update_location
from tgfs.telegram import multi_clients
from tgfs.database import DB
from tgfs.types import FileInfo

log = logging.getLogger(__name__)
routes = web.RouteTableDef()

client_selection_lock = asyncio.Lock()

@routes.get("/")
async def handle_root(_: web.Request):
    return web.json_response({transfer.client_id: [transfer.users] for transfer in multi_clients})

# @routes.get(r"/{msg_id:-?\d+}/{name}")
@routes.get("/dl/{user_id}/{file_id}")
async def handle_file_request(req: web.Request) -> web.Response:
    head: bool = req.method == "HEAD"
    user_id = int(req.match_info["user_id"])
    file_id = int(req.match_info["file_id"])

    transfer: ParallelTransferrer = min(multi_clients, key=lambda c: c.users)
    logging.debug("Using client %s", transfer.client_id)

    file: FileInfo = await DB.db.get_file(file_id, user_id)

    size = file.file_size
    from_bytes = req.http_range.start or 0
    until_bytes = (req.http_range.stop or size) - 1

    if (until_bytes >= size) or (from_bytes < 0) or (until_bytes < from_bytes):
        return web.Response(status=416, headers={"Content-Range": f"bytes */{size}"})
    if head:
        body=None
    else:
        location = await DB.db.get_location(file,  transfer.client_id)
        if location is None:
            source = await DB.db.get_source(file.id, user_id)
            location = await update_location(source, transfer)
        body=transfer.download(location, file.dc_id, size, from_bytes, until_bytes)

    return web.Response(
        status=200 if (from_bytes == 0 and until_bytes == size - 1) else 206,
        body=body,
        headers={
        "Content-Type": file.mime_type,
        "Content-Range": f"bytes {from_bytes}-{until_bytes}/{size}",
        "Content-Length": str(until_bytes - from_bytes + 1),
        "Content-Disposition": f'attachment; filename="{file.file_name}"',
        "Accept-Ranges": "bytes",
    })

@routes.get("/group/{user_id}/{group_id}")
async def handle_file_request(req: web.Request) -> web.Response:
    head: bool = req.method == "HEAD"
    user_id = int(req.match_info["user_id"])
    group_id = int(req.match_info["group_id"])
    group = await DB.db.get_group(group_id, user_id)
    if group is None:
        return web.Response(status=404, text="Group not found")
    resp = "".join(f"{req.scheme}://{req.host}/dl/{user_id}/{file_id}\n" for file_id in group.files)
    return web.Response(status=200, text=resp)