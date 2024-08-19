import argparse
import os
import logging

import requests
from requests.auth import HTTPBasicAuth

# Set logging to debug
logging.basicConfig(level=logging.DEBUG)

def set_environment_variable(var_name, value):
    os.environ[var_name] = value


def load_env_variables():
    """
    Load the environment variables for this session.
    These should be set in your system's .bashrc or .zshrc for persistence.
    """
    username = os.getenv("CLOUD_USERNAME")
    password = os.getenv("CLOUD_PASSWORD")
    tenant = os.getenv("CLOUD_TENANT")

    if not username or not password:
        raise ValueError("Environment variables for credentials are not set.")

    return username, password, tenant


def authenticate_and_get_token(username, password, tenant):
    login_url = f"https://{tenant}.gi-cloud.io/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    auth = HTTPBasicAuth('gibench', '')
    response = requests.post(
        login_url,
        data={"username": username, "password": password, 'grant_type': 'password'},
        headers=headers,
        auth=auth,
    )

    if response.status_code == 200:
        logging.debug("Authentication successful. response: {}".format(response.json()))
        return response.json()["access_token"], response.json()["refresh_token"]
    else:
        raise Exception(
            "Authentication failed. Status code: {}".format(response.status_code)
        )


def main():
    parser = argparse.ArgumentParser(
        description="Authenticate and get a bearer token using cloud credentials."
    )

    parser.add_argument(
        "--username",
        type=str,
        help="Cloud username. If not provided, it will be fetched from the environment.",
    )
    parser.add_argument(
        "--password",
        type=str,
        help="Cloud password. If not provided, it will be fetched from the environment.",
    )
    parser.add_argument("--tenant", type=str, help="Cloud tenant.")

    args = parser.parse_args()

    if args.username:
        set_environment_variable("CLOUD_USERNAME", args.username)
    if args.password:
        set_environment_variable("CLOUD_PASSWORD", args.password)
    if args.tenant:
        set_environment_variable("CLOUD_TENANT", args.tenant)

    try:
        username, password, tenant = load_env_variables()
        print("Environment variables loaded successfully.")
    except ValueError as e:
        print(e)
        return

    # Authenticate and get the bearer token
    try:
        bearer_token, refresh_token = authenticate_and_get_token(username, password, tenant)
        print(f"Bearer Token: {bearer_token}")
    except Exception as e:
        print(f"Failed to authenticate: {e}")


if __name__ == "__main__":
    main()
