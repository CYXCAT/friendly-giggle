from __future__ import annotations

import base64
import json
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import google.auth
import gspread
from google.oauth2.service_account import Credentials


SPREADSHEET_ID = "12bRbTwa8puo1uLs5LdqL2eAcUN4mTNh_i-Bov5xdvw4"
WORKSHEET_GID = 1229268828
SHEETS_SCOPE = "https://www.googleapis.com/auth/spreadsheets"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CREDENTIALS = PROJECT_ROOT / ".secrets" / "sheet-writer.json"
LOCAL_TIMEZONE = ZoneInfo("America/Los_Angeles")


def credentials_path() -> Path:
    configured = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    return Path(configured).expanduser() if configured else DEFAULT_CREDENTIALS


def worksheet() -> gspread.Worksheet:
    encoded_credentials = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON_BASE64")
    path = credentials_path()
    if encoded_credentials:
        service_account_info = json.loads(
            base64.b64decode(encoded_credentials, validate=True).decode("utf-8")
        )
        credentials = Credentials.from_service_account_info(
            service_account_info,
            scopes=[SHEETS_SCOPE],
        )
    elif path.is_file():
        credentials = Credentials.from_service_account_file(
            path,
            scopes=[SHEETS_SCOPE],
        )
    else:
        credentials, _ = google.auth.default(scopes=[SHEETS_SCOPE])
    return gspread.authorize(credentials).open_by_key(
        SPREADSHEET_ID
    ).get_worksheet_by_id(WORKSHEET_GID)


def append_submission(
    your_name: str,
    are_you_a_cat: str,
    makes_biscuits: str,
    can_purr: str,
) -> int:
    timestamp = datetime.now(LOCAL_TIMEZONE).strftime("%Y/%m/%d %H:%M:%S")
    values = [timestamp, are_you_a_cat, makes_biscuits, can_purr, your_name]
    target = worksheet()
    next_row = len(target.get_all_values()) + 1
    target.spreadsheet.batch_update(
        {
            "requests": [
                {
                    "appendCells": {
                        "sheetId": target.id,
                        "rows": [
                            {
                                "values": [
                                    {"userEnteredValue": {"stringValue": value}}
                                    for value in values
                                ]
                            }
                        ],
                        "fields": "userEnteredValue",
                    }
                }
            ]
        }
    )
    return next_row
