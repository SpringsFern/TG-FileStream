from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, AsyncGenerator, List, Optional, Union

from tgfs.utils import InputTypeLocation

# -- MediaInfo
# CREATE TABLE MediaInfo (
#   media_id      BIGINT PRIMARY KEY,
#   size          INT,
#   name          TEXT,
#   mime_type     TEXT,
#   dc_id         INT
#   photo_size    TEXT NULL
# );

# -- Location (per-client session)
# CREATE TABLE Location (
#   media_id        BIGINT,
#   client_id       BIGINT,
#   access_hash     BIGINT,
#   file_reference  BYTEA,
#   PRIMARY KEY (media_id, client_id),
#   FOREIGN KEY (media_id) REFERENCES MediaInfo(media_id) ON DELETE CASCADE
# );

# -- FileInfo (logical file in your app)
# CREATE TABLE FileInfo (
#   id            SERIAL PRIMARY KEY,
#   user_id       BIGINT,
#   chat_id       BIGINT,
#   message_id    BIGINT,
#   media_id      BIGINT,
#   FOREIGN KEY (media_id) REFERENCES MediaInfo(media_id) ON DELETE CASCADE
# );

@dataclass
class MediaInfo:
    media_id: int
    size: int
    name: str
    mime_type:str
    dc_id: int
    photo_size: Optional[str]
    location: Optional[InputTypeLocation]

@dataclass
class FileInfo:
    id: Any
    user_id: int
    chat_id: int
    message_id: int
    media: Optional[MediaInfo]

class FileDB(ABC):
    @abstractmethod
    async def get_file(user_id: int, media_id: int) -> FileInfo:
        pass

    async def get_media(key: int) -> FileInfo:
        pass

    async def iter_files(user_id: int) -> AsyncGenerator[MediaInfo, None]:
        pass
