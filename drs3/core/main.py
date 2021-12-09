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

"""Main business-logic of this service"""

from typing import Callable

from ..config import CONFIG, Config
from ..dao import Database, DrsObjectNotFoundError, ObjectStorage
from ..models import AccessMethod, AccessURL, Checksum, DrsObjectServe


def get_drs_object_serve(
    drs_id: str,
    make_stage_request: Callable[[dict, Config], None],
    config: Config = CONFIG,
):
    """
    Gets the drs object for serving, if it exists in the outbox
    """

    with Database(config=config) as database:
        try:
            db_object_info = database.get_drs_object(drs_id)
        except DrsObjectNotFoundError:  # pylint: disable=try-except-raise
            raise

    # If object exists in Database, see if it exists in outbox

    bucket_id = config.s3_outbox_bucket_id

    with ObjectStorage(config=config) as storage:

        if storage.does_object_exist(bucket_id, drs_id):

            # create presigned url
            download_url = storage.get_object_download_url(bucket_id, drs_id)

            # return DRS Object
            return DrsObjectServe(
                file_id=drs_id,
                self_uri=f"{config.drs_self_url}/{drs_id}",
                size=db_object_info.size,
                created_time=db_object_info.registration_date.isoformat(),
                checksums=[Checksum(checksum=db_object_info.md5_checksum, type="md5")],
                access_methods=[
                    AccessMethod(access_url=AccessURL(url=download_url), type="s3")
                ],
            )

    # If the object does not exist, make a stage request
    make_stage_request(
        db_object_info,
        config,
    )

    return None
