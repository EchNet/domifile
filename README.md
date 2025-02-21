# Prerequisites

Ensure you have the following installed:

* Python 3.9
* Google Cloud SDK (gcloud command)
* Google Apps Script (clasp)
* Ngrok (for local development with OAuth)

# Set up Google Cloud & APIs

Go to console.cloud.google.com and create a new Google Cloud project.

Enable the following APIs:

* Google Drive API
* Google Docs API
* Google Sheets API.
* Google Vision API
* Google Vision AI API.

Create OAuth 2.0 Client Credentials (under APIs & Services > Credentials).
Hang on to the `client_secrets.json` file.

Create a secret in Secret Manager:
```
  gcloud secrets create domifile-oauth-tokens --replication-policy="automatic"
```

# Setting Up API Server

The API server...

* Is implemented based on Flask.
* Manages subscriptions and installations.
* Implements a webhook for notification of incoming documents.

To set up the API server (MacOS only):

* Install Xcode Command Line Tools, including "make"

* `cd server`

* Create a virtual environment

* Run make.  Correct any errors that prevent all packages from being loaded.

* Create `.env` by copying `env.example` and editing the file to reflect your settings.

* Run the server

```
flask run
```

Your API will be running on http://127.0.0.1:5000/.

# Frontend (Google Apps Script UI Extension)

* Open Google Drive.
* Click New > More > Google Apps Script.
* Replace Code.gs with the contents of `frontend/code.gs`
* Save and deploy as an add-on.

# Local Testing (Ngrok for OAuth)

To test OAuth authentication, expose your local Flask server using ngrok:

```
ngrok http 5000
```

Copy the generated HTTPS forwarding URL and update your OAuth redirect URI in Google Cloud Console.

# Deploying to Google Cloud

Once tested locally, deploy using Google Cloud Run:

```
gcloud auth login
gcloud config set project your_project_id
gcloud run deploy domofile --source . --platform managed --allow-unauthenticated
```

Your API will be available via a public URL.
