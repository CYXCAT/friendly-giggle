# Info Sheet

This project contains:

- A SwiftUI iOS app for completing and submitting the form.
- A FastAPI backend that writes submissions to Google Sheets.
- Google Sign-In with backend ID-token verification.
- An interactive command-line form as an alternative client.

Local credentials are stored only under `.secrets`. They are excluded from the
Xcode project, Vercel uploads, and version control. Production credentials are
stored as sensitive Vercel environment variables.

## Start the backend

```bash
cd /Users/yingxiao/Documents/info-sheet
source .venv/bin/activate
uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

Check the local backend connection:

```bash
curl http://127.0.0.1:8000/health
```

## Run the iOS app

1. Open `InfoSheetApp.xcodeproj` in Xcode.
2. Select an iPhone or iPhone Simulator.
3. Click Run.

The app submits to `https://info-sheet.vercel.app`. Users must sign in with a
Google account before the form is shown. The app sends the Google ID token to
the backend, which verifies it before accepting a submission.

## Deploy the backend to Vercel

The Vercel project is linked locally. Deploy the production service with:

```bash
cd /Users/yingxiao/Documents/info-sheet
npx vercel --prod
```

The Google service-account document and Google OAuth server client ID are
configured as Production environment variables in Vercel. Never add service
account credentials to source control.

Submissions are appended to the next row in columns `A:E`. The columns are the
timestamp, three answers, and `Your name`.

## Run the command-line form

```bash
cd /Users/yingxiao/Documents/info-sheet
source .venv/bin/activate
python sheets_writer.py
```

The script reads the current header row, creates a timestamp, prompts for each
remaining field, shows a preview, and writes only after confirmation. Press
Enter at confirmation or press `Ctrl+C` to cancel without writing.

## Regenerate the Xcode project

After changing `project.yml`, run:

```bash
xcodegen generate
```
