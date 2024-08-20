import argparse
import os
import logging
from typing import Tuple

import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv, set_key

logging.basicConfig(level=logging.DEBUG)

"""File to authenticate and get a bearer token using cloud credentials. Token default duration is 1 hour."""

def create_env_file_if_not_exists():
    dotenv_file = '.env'
    if not os.path.exists(dotenv_file):
        with open(dotenv_file, 'w') as file:
            file.write("CLOUD_TENANT=\nBEARER_TOKEN=\nREFRESH_TOKEN=\n")
        logging.debug(".env file created with placeholders.")


def delete_env_file():
    dotenv_file = '.env'
    if os.path.exists(dotenv_file):
        os.remove(dotenv_file)
        logging.debug(f"{dotenv_file} has been deleted.")
    else:
        logging.debug(f"{dotenv_file} does not exist.")


def set_environment_variable(var_name, value):
    os.environ[var_name] = value
    dotenv_file = '.env'
    set_key(dotenv_file, var_name, value)


def load_env_variables() -> Tuple[str | None, str | None, str | None]:
    load_dotenv()
    tenant = os.getenv("CLOUD_TENANT")
    bearer_token = os.getenv("BEARER_TOKEN")
    refresh_token = os.getenv("REFRESH_TOKEN")

    if not tenant:
        raise ValueError("Environment variable for tenant is not set.")

    return tenant, bearer_token, refresh_token


def authenticate_and_get_token(username: str, password: str, tenant_url: str):
    login_url = f"{tenant_url}/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    auth = HTTPBasicAuth("gibench", "")
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
        help="Cloud username. If not provided, it must be entered manually.",
    )
    parser.add_argument(
        "--password",
        type=str,
        help="Cloud password. If not provided, it must be entered manually.",
    )
    parser.add_argument("--tenant", type=str, help="Cloud tenant.")

    args = parser.parse_args()

    create_env_file_if_not_exists()

    if args.tenant:
        set_environment_variable("CLOUD_TENANT", args.tenant)

    if not args.username:
        args.username = input("Enter your Cloud username: ")
    if not args.password:
        args.password = input("Enter your Cloud password: ")

    try:
        tenant, _, _ = load_env_variables()
        logging.info("Environment variables loaded successfully.")
    except ValueError as e:
        logging.error(e)
        return

    try:
        bearer_token, refresh_token = authenticate_and_get_token(
            args.username, args.password, tenant
        )
        set_environment_variable("BEARER_TOKEN", bearer_token)
        set_environment_variable("REFRESH_TOKEN", refresh_token)
        logging.info(f"Bearer Token stored in environment: {bearer_token}")
        logging.info(f"Refresh Token stored in environment: {refresh_token}")
    except Exception as e:
        logging.warning(f"Failed to authenticate: {e}")


if __name__ == "__main__":
    main()
