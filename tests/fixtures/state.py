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

"""Test data"""

import uuid
from pathlib import Path
from typing import Dict, List, Optional

from ghga_service_chassis_lib.object_storage_dao_testing import ObjectFixture, calc_md5
from ghga_service_chassis_lib.utils import TEST_FILE_PATHS
from pydantic.types import UUID4

from drs3 import models

from .config import DEFAULT_CONFIG


def get_study_id_example(index: int) -> str:
    "Generate an example study ID."
    return f"mystudy-{index}"


def get_file_id_example(index: int) -> str:
    "Generate an example file ID."
    return f"myfile-{index}"


class FileState:
    def __init__(
        self,
        id: UUID4,
        external_id: str,
        grouping_label: str,
        file_path: Path,
        in_outbox: bool,
        populate_db: bool = True,
        populate_storage: bool = True,
        message: Optional[dict] = None,
    ):
        """
        Initialize file state and create imputed attributes.
        You may set `populate_db` or `populate_storage` to `False` to indicate that this
        file should not be added to the database or the storage respectively.
        """
        self.id = id
        self.external_id = external_id
        self.grouping_label = grouping_label
        self.file_path = file_path
        self.in_outbox = in_outbox
        self.message = message
        self.populate_db = populate_db
        self.populate_storage = populate_storage

        # computed attributes:
        with open(self.file_path, "rb") as file:
            self.content = file.read()

        self.md5 = calc_md5(self.content)
        self.file_info = models.DrsObjectInitial(
            external_id=self.external_id,
            grouping_label=self.grouping_label,
            md5_checksum=self.md5,
            size=1000,  # not the real size
        )

        self.storage_objects: List[ObjectFixture] = []
        if self.in_outbox:
            self.storage_objects.append(
                ObjectFixture(
                    file_path=self.file_path,
                    bucket_id=DEFAULT_CONFIG.s3_outbox_bucket_id,
                    object_id=self.id,
                )
            )


FILES: Dict[str, FileState] = {
    "in_registry": FileState(
        id=uuid.uuid4(),
        external_id=get_file_id_example(0),
        grouping_label=get_study_id_example(0),
        file_path=TEST_FILE_PATHS[0],
        in_outbox=False,
    ),
}
