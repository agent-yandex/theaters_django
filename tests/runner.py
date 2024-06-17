"""Custom runner."""
from types import MethodType
from typing import Any

from django.db import connections
from django.db.backends.base.base import BaseDatabaseWrapper
from django.test.runner import DiscoverRunner


def prepare_db(self):
    """
    Prepare the database by creating a schema if it does not exist.

    Args:
        self: Self
    """
    self.connect()
    self.connection.cursor().execute('CREATE SCHEMA IF NOT EXISTS api_data;')


class PostgresSchemaRunner(DiscoverRunner):
    """Custom test runner for PostgreSQL databases to create a schema before running tests."""

    def setup_databases(self, **kwargs: Any) -> list[tuple[BaseDatabaseWrapper, str, bool]]:
        """
        Set up databases by preparing each connection.

        Args:
            kwargs: Keyword arguments.

        Returns:
            list[tuple[BaseDatabaseWrapper, str, bool]]: List of prepared databases.
        """
        for conn_name in connections:
            connection = connections[conn_name]
            connection.prepare_database = MethodType(prepare_db, connection)
        return super().setup_databases(**kwargs)
