# Info Sheet

This project contains:

- A SwiftUI iOS app for completing and submitting the form.
- A FastAPI backend that writes submissions to Google Sheets.
- Google Sign-In with backend ID-token verification.
- An interactive command-line form as an alternative client.

Local credentials are stored only under `.secrets`. They are excluded from the
Xcode project, Vercel uploads, and version control. Production credentials are
stored as sensitive Vercel environment variables.


