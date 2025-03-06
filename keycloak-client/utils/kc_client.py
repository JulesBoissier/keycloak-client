import os
import sys
from pathlib import Path

sys.path.append(Path(__file__).resolve().parent.parent.__str__())

from keycloak import KeycloakAdmin

from dotenv import load_dotenv

# Load from .env file if it exists
load_dotenv()

# Read variables (fallback to system environment if not in .env)
DE5_KEYCLOAK_ADMIN_PASSWORD = os.getenv("DE5_KEYCLOAK_ADMIN_PASSWORD")
DE5_HOST = os.getenv("DE5_HOST")
DE5_KEYCLOAK_ADMIN_USERNAME = os.getenv("DE5_KEYCLOAK_ADMIN_USERNAME")

admin_pass = DE5_KEYCLOAK_ADMIN_PASSWORD
keycloak_url = f"https://auth-{DE5_HOST}/auth/"


keycloak_admin = KeycloakAdmin(
    server_url=keycloak_url,
    username=DE5_KEYCLOAK_ADMIN_USERNAME,
    password=admin_pass,
    realm_name="dash",
    user_realm_name="master",
    verify=True,
)


def attach_role(role_name, user_id):
    dash_client_id = keycloak_admin.get_client_id("dash")
    va_role_id = keycloak_admin.get_client_role_id(
        client_id=dash_client_id, role_name=role_name
    )
    va_role = {
        "id": va_role_id,
        "name": role_name,
        "composite": False,
        "clientRole": True,
        "containerId": dash_client_id,
    }
    keycloak_admin.assign_client_role(
        client_id=dash_client_id, user_id=user_id, roles=va_role
    )

def create_user(username, email, roles):
    try:
        new_user = keycloak_admin.create_user(
            {
                "email": email,
                "username": username,
                "enabled": True,
                "credentials": [
                    {
                        "value": "temppassword",
                        "type": "password",
                        "temporary": True,
                    }
                ],
            },
            exist_ok=False,
        )
        if not isinstance(roles, str):
            for role in roles:
                print("Attaching new role")
                attach_role(role, new_user)

        return True
    except Exception as e:
        print(
            f"\033[91mCan't create user with this username: {username}."
            f" You can see the reason under this message.\033[0m"
        )
        print(e)
        return False

def list_all_users():

    try:

        formatted_users = []
        client_id = keycloak_admin.get_client_id("dash")
        users = keycloak_admin.get_users()
        for user in users:
            user_id = user["id"]
            roles = keycloak_admin.get_client_roles_of_user(client_id = client_id, user_id = user_id)
            formatted_users.append({
                "ID": user.get("id", "N/A"),
                "Name": user.get("username", "N/A"),
                "Email": user.get("email", "N/A"),
                "Roles": ", ".join([role["name"] for role in roles]) if roles else "No roles"
            })
        return formatted_users

    except Exception as e:
        print(f"\033[91mError fetching Keycloak users: {e}\033[0m")
        return []


def delete_user(user_id):
    try:
        keycloak_admin.delete_user(user_id)
        print(f"User {user_id} deleted successfully.")
        return True
    except Exception as e:
        print(f"\033[91mFailed to delete user {user_id}: {e}\033[0m")
        return False