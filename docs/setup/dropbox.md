# Dropbox Setup

Castoria supports uploading downloaded audio to Dropbox using the official Dropbox API.

Dropbox integration uses **App Folder** access to restrict Castoria's access to its dedicated application directory.

Authentication uses OAuth 2.0 with a Refresh Token. Configuration is completed once during setup, and the Dropbox SDK automatically refreshes Access Tokens when necessary.

## 1. Create a Dropbox App

1. Visit the [Dropbox App Console](https://www.dropbox.com/developers/apps).
2. Click **Create app**.
3. Select **Scoped access**.
4. Choose **App folder** as the access type.
5. Enter an application name, such as `Castoria`.
6. Create the application.

Dropbox creates a dedicated application directory:

```text
Dropbox/
└── Apps/
    └── Castoria/
```

All Dropbox paths provided to Castoria are relative to this directory.

## 2. Configure API Permissions

Open your application in the Dropbox App Console and navigate to **Permissions**.

Enable the following scopes:

| Scope | Purpose |
| --- | --- |
| `files.content.write` | Upload audio files to Dropbox. |
| `files.metadata.read` | Retrieve file and folder metadata. |

Click **Submit** to save your changes.

No Full Dropbox access is required.

## 3. Obtain an Authorization Code

Open the following URL in your browser, replacing `YOUR_APP_KEY` with your Dropbox application's App Key:

```text
https://www.dropbox.com/oauth2/authorize?client_id=YOUR_APP_KEY&response_type=code&token_access_type=offline
```

Sign in to Dropbox and authorize the application.

Dropbox displays **Access Code Generated**, followed by an Authorization Code.

Copy the Authorization Code for the next step.

> The Authorization Code is temporary, can only be used once, and is not the Refresh Token.

## 4. Exchange the Authorization Code for a Refresh Token

Open a terminal and run:

```bash
read -r -p "Dropbox App Key: " APP_KEY
read -r -s -p "Dropbox App Secret: " APP_SECRET
echo
read -r -s -p "Authorization Code: " AUTH_CODE
echo

curl --fail-with-body --silent --show-error \
  --request POST "https://api.dropboxapi.com/oauth2/token" \
  --user "$APP_KEY:$APP_SECRET" \
  --data-urlencode "code=$AUTH_CODE" \
  --data-urlencode "grant_type=authorization_code"

unset APP_KEY APP_SECRET AUTH_CODE
```

The API returns a JSON response similar to:

```json
{
  "access_token": "sl.xxxxx",
  "token_type": "bearer",
  "expires_in": 14400,
  "refresh_token": "xxxxxxxx",
  "scope": "files.content.write files.metadata.read"
}
```

Save the value of `refresh_token`.

**Important:**

- `access_token` is short-lived and should not be used as the permanent credential.
- `refresh_token` allows the Dropbox SDK to obtain new Access Tokens automatically.
- Never share your App Secret, Authorization Code, or Refresh Token.
- If the Authorization Code expires or has already been used, generate a new one.

## 5. Configure Environment Variables

Add the following variables to Castoria's `.env` file:

```dotenv
CASTORIA_DROPBOX_APP_KEY=your_app_key
CASTORIA_DROPBOX_APP_SECRET=your_app_secret
CASTORIA_DROPBOX_REFRESH_TOKEN=your_refresh_token
```

Ensure `.env` is included in `.gitignore`.

Do not commit credentials to version control.

## 6. Using Dropbox Storage

Once configured, Dropbox can be selected as a storage provider:

```bash
castoria youtube-music download \
  --link "https://www.youtube.com/watch?v=VIDEO_ID" \
  --storage dropbox \
  --dest "/Music" \
  --name "my-audio"
```

With App Folder access, the destination `/Music` corresponds to:

```text
Dropbox/
└── Apps/
    └── Castoria/
        └── Music/
            └── my-audio.m4a
```

Castoria uses the configured Refresh Token to authenticate automatically.

No additional OAuth authorization is required during normal operation unless the authorization is revoked or becomes invalid.
