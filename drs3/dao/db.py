# Copyright 2021 Universität Tübingen, DKFZ and EMBL
# for the German Human Genome-Phenome Archive (GHGA)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Database DAO"""

from datetime import datetime
from typing import Any, Optional

from ghga_service_chassis_lib.postgresql import (
    PostgresqlConfigBase,
    SyncPostgresqlConnector,
)
from ghga_service_chassis_lib.utils import DaoGenericBase
from sqlalchemy.future import select

from .. import models
from ..config import CONFIG
from . import db_models

psql_connector = SyncPostgresqlConnector(CONFIG)


class DrsObjectNotFoundError(RuntimeError):
    """Thrown when trying to access a DrsObject with an external ID that doesn't
    exist in the database."""

    def __init__(self, external_id: Optional[str]):
        message = (
            "The DRS Object"
            + (f" with external ID '{external_id}' " if external_id else "")
            + " does not exist in the database."
        )
        super().__init__(message)


class DrsObjectAlreadyExistsError(RuntimeError):
    """Thrown when trying to create a new DrsObject with an external ID that already
    exist in the database."""

    def __init__(self, external_id: Optional[str]):
        message = (
            "The DRS object"
            + (f" with external ID '{external_id}' " if external_id else "")
            + " already exist in the database."
        )
        super().__init__(message)


# Since this is just a DAO stub without implementation, following pylint error are
# expected:
# pylint: disable=unused-argument,no-self-use
class DatabaseDao(DaoGenericBase):
    """
    A DAO base class for interacting with the database.

    It might throw following exception to communicate selected error events:
        - DrsObjectNotFoundError
        - DrsObjectAlreadyExistsError
    """

    def get_drs_object(self, external_id: str) -> models.DrsObjectInternal:
        """Get DRS object from the database"""
        ...

    def register_drs_object(self, drs_object: models.DrsObjectInitial) -> None:
        """Register a new DRS object to the database."""
        ...

    def unregister_drs_object(self, external_id: str) -> None:
        """
        Unregister a new DRS object with the specified external ID from the database.
        """
        ...


class PostgresDatabase(DatabaseDao):
    """
    An implementation of the  DatabaseDao interface using a PostgreSQL backend.
    """

    def __init__(self, config: PostgresqlConfigBase = CONFIG):
        """initialze DAO implementation"""

        super().__init__()
        self._postgresql_connector = SyncPostgresqlConnector(config)

        # will be defined on __enter__:
        self._session_cm: Any = None
        self._session: Any = None

    def __enter__(self):
        """Setup database connection"""

        self._session_cm = self._postgresql_connector.transactional_session()
        self._session = self._session_cm.__enter__()
        return self

    def __exit__(self, error_type, error_value, error_traceback):
        """Teardown database connection"""
        self._session_cm.__exit__(error_type, error_value, error_traceback)

    def _get_orm_drs_object(self, external_id: str) -> db_models.DrsObject:
        """Internal method to get the ORM representation of a drs object by specifying
        its external ID"""

        statement = select(db_models.DrsObject).filter_by(external_id=external_id)
        orm_drs_object = self._session.execute(statement).scalars().one_or_none()

        if orm_drs_object is None:
            raise DrsObjectNotFoundError(external_id=external_id)

        return orm_drs_object

    def get_drs_object(self, external_id: str) -> models.DrsObjectInternal:
        """Get DRS object from the database"""

        orm_drs_object = self._get_orm_drs_object(external_id=external_id)
        return models.DrsObjectInternal.from_orm(orm_drs_object)

    def register_drs_object(self, drs_object: models.DrsObjectInitial) -> None:
        """Register a new DRS object to the database."""

        # check for collisions in the database:
        try:
            self._get_orm_drs_object(external_id=drs_object.external_id)
        except DrsObjectNotFoundError:
            # this is expected
            pass
        else:
            # this is a problem
            raise DrsObjectAlreadyExistsError(external_id=drs_object.external_id)

        drs_object_dict = {
            **drs_object.dict(),
            "registration_date": datetime.now(),
        }
        orm_drs_object = db_models.DrsObject(**drs_object_dict)
        self._session.add(orm_drs_object)

    def unregister_drs_object(self, external_id: str) -> None:
        """
        Unregister a new DRS object with the specified external ID from the database.
        """

        orm_drs_object = self._get_orm_drs_object(external_id=external_id)
        self._session.delete(orm_drs_object)
