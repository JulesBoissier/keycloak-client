import sys
from pathlib import Path

sys.path.append(Path(__file__).resolve().parent.parent.__str__())

from keycloak import KeycloakAdmin

DE5_KEYCLOAK_ADMIN_PASSWORD = "P3fMNAJ3hkl7MpcyRITd"
DE5_HOST = "tam.plotly.host"
DE5_KEYCLOAK_ADMIN_USERNAME = "admin"


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

def create_user(user):
    try:
        new_user = keycloak_admin.create_user(
            {
                "email": "test@example.com",
                "username": "JulesTest",
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
        attach_role("licensed_user", new_user)

        return True
    except Exception as e:
        print(
            f"\033[91mCan't create user with this username: {user['username']}."
            f" You can see the reason under this message.\033[0m"
        )
        print(e)
        return False


if __name__ == "__main__":

    user = {"username": "JulesTest"}
    is_created = create_user(user)

    if is_created:
        print(f"created {user}")