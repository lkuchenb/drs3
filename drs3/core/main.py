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


def get_drs_object(drs_id: str, make_stage_request: Callable, config: Config = CONFIG):

    
    object_id = request.matchdict["object_id"]
    config: Config = CONFIG

    with Database(config=config) as database:
        try:
            db_object_info = database.get_drs_object(object_id)
        except DrsObjectNotFoundError as object_not_found_error:
            raise HTTPNotFound(
                json={
                    "msg": "The requested DRSObject does not exist",
                    "status_code": 404,
                }
            ) from object_not_found_error

    # If object exists in Database, see if it exists in outbox

    bucket_id = config.s3_outbox_bucket_id

    with ObjectStorage(config=config) as storage:
        if storage.does_object_exist(bucket_id, object_id):

            # create presigned url
            response = storage.get_object_download_url(bucket_id, object_id)

            # change path to localhost
            path = "http://localhost:4566" + response.removeprefix(
                config.s3_endpoint_url
            )

            return DrsObjectServe(
                id=object_id,
                self_uri=f"{config.drs_self_url}/{object_id}",
                size=db_object_info.size,
                created_time=db_object_info.registration_date,
                checksums=[Checksum(checksum=db_object_info.md5_checksum, type="md5")],
                access_methods=[
                    AccessMethod(access_url=AccessURL(url=path), type="s3")
                ],
            )
    

    make_stage_request(DrsObjectInternal(...), config)
    