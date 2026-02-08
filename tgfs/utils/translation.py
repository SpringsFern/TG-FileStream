
from typing import Union

from tgfs.utils.types import User

class en:
    # ── Start & Help ─────────────────────────────────────────────
    START_TEXT = """Send me any telegram file or photo I will generate a link for it
Use /help to see available commands."""

    HELP_TEXT = """
Available Commands:
/start - Start the bot
/help - Show this help message
/group - Start creating a group of files
/done - Finish adding files to the group
/files - List your uploaded files or created groups
"""

    ACCEPTED_TOS_TEXT = "You have agreed to the Terms of Service."

    # ── Errors & State ────────────────────────────────────────────
    UNKNOWN_COMMAND = "Unknown command/operation"
    SOMETHING_WENT_WRONG = "Something went wrong. Please try again later."
    INAVLID_LINK_TEXT = "Invalid link."
    INVALID_PAGE = "Invalid page."

    ALREADY_IN_OP = "You are already in an operation. Please complete it before starting a new one."
    NOT_IN_OP = "You are not in any operation."

    FILE_ID_NOT_FOUND = "File with id `{file_id}` not found."
    FILE_LOCATION_NOT_FOUND = "File location not found."
    FILE_NOT_FOUND_TEXT = "File not found."
    GROUP_NOT_FOUND_TEXT = "Group not found."

    # ── File & Group Info ─────────────────────────────────────────
    FILES_TEXT = """You have created links for:
• Files: {total_files}
• Groups: {total_groups}

Select the type of links you want to view.
"""

    FILE_INFO_TEXT = """File Info:
ID: {file_id}
DC ID: {dc_id}
Size: {file_size} bytes
MIME Type: {mime_type}
File Name: {file_name}
File Type: {file_type}
Is Restricted: {restricted}"""

    GROUP_INFO_TEXT = """Group Info:
Name: {name}
Created At: {created_at}
Total Files: {total_files}"""

    # ── Group Flow ────────────────────────────────────────────────
    GROUP_NAME_TEXT = "Send a name for your group of files"
    GROUP_SENDFILE_TEXT = "Send files to add to the group. When done, send /done"
    GROUP_CREATED_TEXT = "Group '{name}' created!\n{url}"
    GROUP_NOFILES_TEXT = "No files were added to the group. Operation cancelled."
    GROUP_ENDOF_FILES = "End of group files."

    # ── File Actions ──────────────────────────────────────────────
    CONFIRM_DELETE_TEXT = "Do you really want to delete this file?"
    FILE_DELETED_SUCCESSFULLY = "File deleted successfully."
    SELECT_TYPE_OF_FILE = "Select the type of links you want to view."
    GET_FILE_TEXT = "Get File"

    # ── Lists & Pagination ────────────────────────────────────────
    NO_LABEL_LINKS_TEXT = "You have not generated any {label} links yet."
    NO_LABELS_TEXT = "No {label}s on this page."
    TOTAL_LABEL_COUNT = "You have **{total}** {label}s."
    FILES_BUTTON_CURRENT = "Page {page_no}/{total_pages}."

    # ── Buttons & Labels ──────────────────────────────────────────
    YES = "Yes"
    NO = "No"
    BACK_TEXT = "Back"

    PHOTO = "Photo"
    DOCUMENT = "Document"

    DELETE = "Delete"
    OPEN = "Open"

    DOWNLOAD = "Download"
    FILES = "Files"
    GROUPS = "Groups"
    AGREED = "Agreed"
    EXTERNAL_LINK = "External Link"



registry = {
    "en": en
}

def get_lang(iso_code: Union[str, User] = None) -> en:
    if isinstance(iso_code, User):
        iso_code = iso_code.preferred_lang
    return registry.get(iso_code, en)
