import logging
from collections import defaultdict
from typing import Callable, Any
from enum import Enum

log = logging.getLogger("events")

class Events(Enum):
    STARTUP = "startup"
    AFTER_WEBAPP = "after_webapp"
    REQUEST = "request"

HANDLER=dict[Events, list[Callable[..., Any]]]

_register_blocking: HANDLER = defaultdict(list)
_register_background: HANDLER = defaultdict(list)
_hook_blocking: HANDLER = defaultdict(list)
_hook_background: HANDLER = defaultdict(list)
