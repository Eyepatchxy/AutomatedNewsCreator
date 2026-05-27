from paths import OAUTH_DIR, TOKEN_FILE
from google_auth_oauthlib.flow import InstalledAppFlow


SCOPES = ["https://www.googleapis.com/auth/youtube"]
BASE_DIR = OAUTH_DIR


def find_client_secret():
    client_files = sorted(BASE_DIR.glob("client_secret*.json"))
    if not client_files:
        raise FileNotFoundError(f"No client_secret*.json file found in {BASE_DIR}")
    return client_files[0]


def main():
    client_file = find_client_secret()

    print(f"Using client file: {client_file}")
    print(f"Token will be saved to: {TOKEN_FILE}")
    print("Opening browser for YouTube OAuth consent...")

    flow = InstalledAppFlow.from_client_secrets_file(str(client_file), SCOPES)
    creds = flow.run_local_server(
        port=0,
        prompt="consent",
        access_type="offline",
    )

    TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")

    print(f"Saved token: {TOKEN_FILE}")
    print(f"Has refresh token: {bool(creds.refresh_token)}")


if __name__ == "__main__":
    main()
