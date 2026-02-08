
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
/setln - Change your language
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

    # ── Languages ─────────────────────────────────────────────────
    SETLN_USAGE_TEXT = "/setln <language_code>\nExample: /setln en\nSupported language codes: {supported_codes}"
    SETLN_SET_TO = "Language changed to {ln_code}"

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

class kn(en):
    # ── Start & Help ─────────────────────────────────────────────
    START_TEXT = """ಯಾವುದೇ ಟೆಲಿಗ್ರಾಂ ಕಡತ ಅಥವಾ ಚಿತ್ರವನ್ನು ನನಗೆ ಕಳುಹಿಸಿ, ಅದಕ್ಕೆ ನಾನು ಒಂದು ಲಿಂಕ್ ರಚಿಸುತ್ತೇನೆ.
ಲಭ್ಯವಿರುವ ಆಜ್ಞೆಗಳನ್ನು ನೋಡಲು /help ಬಳಸಿ."""

    HELP_TEXT = """
ಲಭ್ಯವಿರುವ ಆಜ್ಞೆಗಳು:
/start - ಬಾಟ್ ಅನ್ನು ಪ್ರಾರಂಭಿಸಿ
/help - ಈ ಸಹಾಯ ಸಂದೇಶವನ್ನು ತೋರಿಸಿ
/group - ಕಡತಗಳ ಗುಂಪನ್ನು ರಚಿಸಲು ಪ್ರಾರಂಭಿಸಿ
/done - ಗುಂಪಿಗೆ ಕಡತಗಳನ್ನು ಸೇರಿಸುವುದನ್ನು ಪೂರ್ಣಗೊಳಿಸಿ
/files - ನೀವು ಕಳುಹಿಸಿದ ಕಡತಗಳ ಮತ್ತು ರಚಿಸಿದ ಗುಂಪುಗಳ ಪಟ್ಟಿ
/setln - ನಿಮ್ಮ ಭಾಷೆಯನ್ನು ಬದಲಾಯಿಸಲು
"""

    ACCEPTED_TOS_TEXT = "ನೀವು ಸೇವಾ ನಿಯಮಗಳಿಗೆ ಒಪ್ಪಿಗೆ ನೀಡಿದ್ದೀರಿ."

    # ── Errors & State ────────────────────────────────────────────
    UNKNOWN_COMMAND = "ಅಪರಿಚಿತ ಆಜ್ಞೆ / ಕಾರ್ಯ"
    SOMETHING_WENT_WRONG = "ಏನೋ ತಪ್ಪಾಗಿದೆ. ದಯವಿಟ್ಟು ನಂತರ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ."
    INAVLID_LINK_TEXT = "ಅಮಾನ್ಯ ಲಿಂಕ್."
    INVALID_PAGE = "ಅಮಾನ್ಯ ಪುಟ."

    ALREADY_IN_OP = "ನೀವು ಈಗಾಗಲೇ ಒಂದು ಕಾರ್ಯದಲ್ಲಿದ್ದೀರಿ. ಹೊಸದನ್ನು ಪ್ರಾರಂಭಿಸುವ ಮೊದಲು ಅದನ್ನು ಪೂರ್ಣಗೊಳಿಸಿ."
    NOT_IN_OP = "ನೀವು ಯಾವುದೇ ಕಾರ್ಯದಲ್ಲಿಲ್ಲ."

    FILE_ID_NOT_FOUND = "`{file_id}` ಗುರುತಿನ ಯಾವುದೇ ಫೈಲ್ ಕಂಡುಬಂದಿಲ್ಲ."
    FILE_LOCATION_NOT_FOUND = "ಕಡತದ ಸ್ಥಳ ಕಂಡುಬಂದಿಲ್ಲ."
    FILE_NOT_FOUND_TEXT = "ಕಡತ ಕಂಡುಬಂದಿಲ್ಲ."
    GROUP_NOT_FOUND_TEXT = "ಗುಂಪು ಕಂಡುಬಂದಿಲ್ಲ."

    # ── File & Group Info ─────────────────────────────────────────
    FILES_TEXT = """ನೀವು ರಚಿಸಿದ ಲಿಂಕ್‌ಗಳು :
• ಕಡತಗಳು: {total_files}
• ಗುಂಪುಗಳು: {total_groups}

ನೀವು ನೋಡಲು ಬಯಸುವ ಲಿಂಕ್‌ಗಳ ಪ್ರಕಾರವನ್ನು ಆಯ್ಕೆಮಾಡಿ.
"""

    FILE_INFO_TEXT = """ಫೈಲ್ ಮಾಹಿತಿ:
ಕಡತದ ಐಡಿ: {file_id}
ಡಿಸಿ ಐಡಿ: {dc_id}
ಗಾತ್ರ: {file_size} ಬೈಟ್‌ಗಳು
ಮೈಮ್ ಪ್ರಕಾರ: {mime_type}
ಕಡತದ ಹೆಸರು: {file_name}
ಕಡತದ ಪ್ರಕಾರ: {file_type}
ನಿರ್ಬಂಧಿತವಾಗಿದೆ: {restricted}"""

    GROUP_INFO_TEXT = """ಗುಂಪು ಮಾಹಿತಿ:
ಹೆಸರು: {name}
ರಚಿಸಿದ ದಿನಾಂಕ: {created_at}
ಒಟ್ಟು ಕಡತಗಳು: {total_files}"""

    # ── Group Flow ────────────────────────────────────────────────
    GROUP_NAME_TEXT = "ನಿಮ್ಮ ಕಡತಗಳ ಗುಂಪಿಗೆ ಒಂದು ಹೆಸರನ್ನು ಕಳುಹಿಸಿ"
    GROUP_SENDFILE_TEXT = "ಗುಂಪಿಗೆ ಸೇರಿಸಲು ಕಡತಗಳನ್ನು ಕಳುಹಿಸಿ. ಮುಗಿದ ನಂತರ /done ಕಳುಹಿಸಿ"
    GROUP_CREATED_TEXT = "ಗುಂಪು '{name}' ರಚಿಸಲಾಗಿದೆ!\n{url}"
    GROUP_NOFILES_TEXT = "ಗುಂಪಿಗೆ ಯಾವುದೇ ಕಡತಗಳನ್ನು ಸೇರಿಸಲಾಗಿಲ್ಲ. ಕಾರ್ಯವನ್ನು ರದ್ದುಗೊಳಿಸಲಾಗಿದೆ."
    GROUP_ENDOF_FILES = "ಗುಂಪಿನ ಕಡತಗಳ ಅಂತ್ಯ."

    # ── File Actions ──────────────────────────────────────────────
    CONFIRM_DELETE_TEXT = "ನೀವು ಈ ಕಡತ ಅನ್ನು ಅಳಿಸಲು ಖಚಿತವಾಗಿದ್ದೀರಾ?"
    FILE_DELETED_SUCCESSFULLY = "ಕಡತ ಯಶಸ್ವಿಯಾಗಿ ಅಳಿಸಲಾಗಿದೆ."
    SELECT_TYPE_OF_FILE = "ನೀವು ನೋಡಲು ಬಯಸುವ ಲಿಂಕ್‌ಗಳ ಪ್ರಕಾರವನ್ನು ಆಯ್ಕೆಮಾಡಿ."
    GET_FILE_TEXT = "ಕಡತದ ಪಡೆಯಿರಿ"

    # ── Lists & Pagination ────────────────────────────────────────
    NO_LABEL_LINKS_TEXT = "ನೀವು ಇನ್ನೂ ಯಾವುದೇ {label} ಲಿಂಕ್‌ಗಳನ್ನು ರಚಿಸಿಲ್ಲ."
    NO_LABELS_TEXT = "ಈ ಪುಟದಲ್ಲಿ ಯಾವುದೇ {label}ಗಳಿಲ್ಲ."
    TOTAL_LABEL_COUNT = "ನಿಮ್ಮ ಬಳಿ ಒಟ್ಟು **{total}** {label}ಗಳಿವೆ."
    FILES_BUTTON_CURRENT = "ಪುಟ {page_no}/{total_pages}."

    # ── Languages ─────────────────────────────────────────────────
    SETLN_USAGE_TEXT = "/setln <language_code>\nಉದಾಹರಣೆ: /setln en\nಬೆಂಬಲಿತ ಭಾಷಾ ಕೋಡ್‌ಗಳು: {supported_codes}"
    SETLN_SET_TO = "ಭಾಷೆಯನ್ನು {ln_code} ಗೆ ಬದಲಾಯಿಸಲಾಗಿದೆ"

    # ── Buttons & Labels ──────────────────────────────────────────
    YES = "ಹೌದು"
    NO = "ಇಲ್ಲ"
    BACK_TEXT = "ಹಿಂತಿರುಗಿ"

    PHOTO = "ಚಿತ್ರ"
    DOCUMENT = "ದಾಖಲೆ"

    DELETE = "ಅಳಿಸಿ"
    OPEN = "ತೆರೆಯಿರಿ"

    DOWNLOAD = "ಡೌನ್‌ಲೋಡ್"
    FILES = "ಕಡತಗಳು"
    GROUPS = "ಗುಂಪುಗಳು"
    AGREED = "ಒಪ್ಪಿಗೆ"
    EXTERNAL_LINK = "ಬಾಹ್ಯ ಲಿಂಕ್"

registry = {
    "en": en,
    "kn": kn
}

def get_lang(iso_code: Union[str, User] = None) -> en:
    if isinstance(iso_code, User):
        iso_code = iso_code.preferred_lang
    return registry.get(iso_code, en)
