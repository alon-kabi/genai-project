import os
from abc import ABC, abstractmethod


class MssqlBackend(ABC):
    placeholder = "%s"

    def __init__(self):
        self.server = os.getenv("MSSQL_SERVER", "localhost")
        self.database = os.getenv("MSSQL_DATABASE")
        self.user = os.getenv("MSSQL_USER")
        self.password = os.getenv("MSSQL_PASSWORD")

    @abstractmethod
    def connect(self):
        """Open and return a database connection."""

    def adapt_query(self, query: str) -> str:
        return query.replace("%s", self.placeholder)


class PyodbcBackend(MssqlBackend):
    placeholder = "?"

    def connect(self):
        import pyodbc

        driver = os.getenv("MSSQL_DRIVER", "ODBC Driver 17 for SQL Server")
        connection_string = (
            f"DRIVER={{{driver}}};"
            f"SERVER={self.server};"
            f"DATABASE={self.database};"
            f"UID={self.user};"
            f"PWD={self.password};"
            "TrustServerCertificate=yes;"
        )
        return pyodbc.connect(connection_string, timeout=10)


class PymssqlBackend(MssqlBackend):
    placeholder = "%s"

    def connect(self):
        import pymssql

        return pymssql.connect(
            server=self.server,
            user=self.user,
            password=self.password,
            database=self.database,
        )


def get_mssql_backend() -> MssqlBackend:
    backend = os.getenv("MSSQL_BACKEND", "pymssql").strip().lower()
    if backend == "pyodbc":
        return PyodbcBackend()
    if backend == "pymssql":
        return PymssqlBackend()
    raise ValueError(
        f"Unsupported MSSQL_BACKEND '{backend}'. Use 'pyodbc' or 'pymssql'."
    )
