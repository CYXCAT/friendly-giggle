#!/usr/bin/env python3
"""Collect values interactively and append them to a Google Sheet."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import google.auth
from google.auth import impersonated_credentials
import gspread


SPREADSHEET_ID = "12bRbTwa8puo1uLs5LdqL2eAcUN4mTNh_i-Bov5xdvw4"
WORKSHEET_GID = 1229268828
SERVICE_ACCOUNT = "sheet-writer@sso-511121.iam.gserviceaccount.com"
CLOUD_SCOPE = "https://www.googleapis.com/auth/cloud-platform"
SHEETS_SCOPE = "https://www.googleapis.com/auth/spreadsheets"
LOCAL_TIMEZONE = ZoneInfo("America/Los_Angeles")


def get_worksheet() -> gspread.Worksheet:
    """Use local ADC to impersonate the service account without a JSON key."""
    source_credentials, _ = google.auth.default(scopes=[CLOUD_SCOPE])
    credentials = impersonated_credentials.Credentials(
        source_credentials=source_credentials,
        target_principal=SERVICE_ACCOUNT,
        target_scopes=[SHEETS_SCOPE],
        lifetime=3600,
    )
    client = gspread.authorize(credentials)
    return client.open_by_key(SPREADSHEET_ID).get_worksheet_by_id(WORKSHEET_GID)


def collect_values(headers: list[str]) -> list[str]:
    """Generate a timestamp and prompt for every remaining column."""
    timestamp = datetime.now(LOCAL_TIMEZONE).strftime("%Y/%m/%d %H:%M:%S")
    values = [timestamp]

    print("\nEnter the following values. Press Enter to leave a field blank:\n")
    for header in headers[1:]:
        values.append(input(f"{header}: ").strip())

    return values


def confirm(headers: list[str], values: list[str]) -> bool:
    print("\nReady to submit:")
    display_headers = ["Timestamp", *headers[1:]]
    for header, value in zip(display_headers, values):
        print(f"  {header}: {value or '(blank)'}")

    answer = input("\nSubmit this row? [y/N]: ").strip().lower()
    return answer in {"y", "yes"}


def main() -> None:
    try:
        worksheet = get_worksheet()
        headers = worksheet.row_values(1)
        if len(headers) < 2:
            raise RuntimeError("The worksheet header is empty or has too few fields.")

        values = collect_values(headers)
        if not confirm(headers, values):
            print("Cancelled. No data was written.")
            return

        result = worksheet.append_row(values, value_input_option="USER_ENTERED")
        updated_range = result["updates"]["updatedRange"]
        print(f"Saved successfully: {updated_range}")
    except KeyboardInterrupt:
        print("\nCancelled. No data was written.")
    except gspread.exceptions.APIError as error:
        raise SystemExit(f"Google Sheets API request failed: {error}") from error


if __name__ == "__main__":
    main()
