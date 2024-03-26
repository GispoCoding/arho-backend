import enum
import json
import os
from typing import Dict, List, Optional, Tuple, Type

import boto3


class User(enum.Enum):
    SU = "DB_SECRET_SU_ARN"
    ADMIN = "DB_SECRET_ADMIN_ARN"
    READ_WRITE = "DB_SECRET_RW_ARN"
    READ = "DB_SECRET_R_ARN"


class Db(enum.Enum):
    MAINTENANCE = 1
    MAIN = 2


class DatabaseHelper:
    def __init__(self, user: Optional[User] = None):
        """
        Initialize a database helper with given user privileges.

        If user is not specified, requires that the lambda function has *all* user
        privileges and secrets specified in lambda function os.environ.
        """
        if os.environ.get("READ_FROM_AWS", "1") == "1":
            session = boto3.session.Session()
            client = session.client(
                service_name="secretsmanager",
                region_name=os.environ.get("AWS_REGION_NAME"),
            )
            # if user is not specified, iterate through all users
            users: List | Type[User] = [user] if user else User
            self._users = {
                user: json.loads(
                    client.get_secret_value(SecretId=os.environ[user.value])[
                        "SecretString"
                    ]
                )
                for user in users
            }
        else:
            self._users = {
                User.SU: {
                    "username": os.environ.get("SU_USER"),
                    "password": os.environ.get("SU_USER_PW"),
                },
                User.ADMIN: {
                    "username": os.environ.get("ADMIN_USER"),
                    "password": os.environ.get("ADMIN_USER_PW"),
                },
                User.READ_WRITE: {
                    "username": os.environ.get("RW_USER"),
                    "password": os.environ.get("RW_USER_PW"),
                },
                User.READ: {
                    "username": os.environ.get("R_USER"),
                    "password": os.environ.get("R_USER_PW"),
                },
            }
        self._dbs = {
            Db.MAIN: os.environ["DB_MAIN_NAME"],
            Db.MAINTENANCE: os.environ["DB_MAINTENANCE_NAME"],
        }
        self._host = os.environ["DB_INSTANCE_ADDRESS"]
        self._port = os.environ.get("DB_INSTANCE_PORT", "5432")
        self._region_name = os.environ.get("AWS_REGION_NAME")

    def get_connection_parameters(
        self, user: Optional[User] = None, db: Db = Db.MAIN
    ) -> Dict[str, str]:
        if not user:
            # take the first user that has credentials provided
            user = next(iter(self._users))
        user_credentials = self._users[user]
        return {
            "host": self._host,
            "port": self._port,
            "dbname": self.get_db_name(db),
            "user": user_credentials["username"],
            "password": user_credentials["password"],
        }

    def get_connection_string(self) -> str:
        db_params = self.get_connection_parameters()
        return (
            f'postgresql://{db_params["user"]}:{db_params["password"]}'
            f'@{db_params["host"]}:{db_params["port"]}/{db_params["dbname"]}'
        )

    def get_username_and_password(self, user: User) -> Tuple[str, str]:
        user_credentials = self._users[user]
        return user_credentials["username"], user_credentials["password"]

    def get_db_name(self, db: Db) -> str:
        return self._dbs[db]

    def get_users(self) -> Dict[User, dict]:
        return self._users
