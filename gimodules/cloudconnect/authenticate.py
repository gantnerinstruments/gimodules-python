import argparse
import os
import logging
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv, set_key, dotenv_values

logging.basicConfig(level=logging.DEBUG)

def create_env_file_if_not_exists():
    dotenv_file = '.env'
    if not os.path.exists(dotenv_file):
        with open(dotenv_file, 'w') as file:
            file.write("CLOUD_USERNAME=\nCLOUD_PASSWORD=\nCLOUD_TENANT=\n")
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

def load_env_variables():
    load_dotenv()
    username = os.getenv("CLOUD_USERNAME")
    password = os.getenv("CLOUD_PASSWORD")
    tenant = os.getenv("CLOUD_TENANT")

    if not username or not password or not tenant:
        raise ValueError("Environment variables for credentials are not set.")

    return username, password, tenant

def authenticate_and_get_token(username, password, tenant):
    login_url = f"https://{tenant}.gi-cloud.io/token"
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
        help="Cloud username. If not provided, it will be fetched from the environment.",
    )
    parser.add_argument(
        "--password",
        type=str,
        help="Cloud password. If not provided, it will be fetched from the environment.",
    )
    parser.add_argument("--tenant", type=str, help="Cloud tenant.")

    args = parser.parse_args()

    create_env_file_if_not_exists()

    if args.username:
        set_environment_variable("CLOUD_USERNAME", args.username)
    if args.password:
        set_environment_variable("CLOUD_PASSWORD", args.password)
    if args.tenant:
        set_environment_variable("CLOUD_TENANT", args.tenant)

    try:
        username, password, tenant = load_env_variables()
        logging.info("Environment variables loaded successfully.")
    except ValueError as e:
        print(e)
        return

    try:
        bearer_token, refresh_token = authenticate_and_get_token(
            username, password, tenant
        )
        logging.info(f"Bearer Token: {bearer_token}")
    except Exception as e:
        logging.warning(f"Failed to authenticate: {e}")

if __name__ == "__main__":
    main()
