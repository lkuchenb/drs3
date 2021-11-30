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

"""
Subscriptions to async topics
"""

import json
from pathlib import Path

import pika
from ghga_service_chassis_lib.pubsub import AmqpTopic

from ..config import Config, config
from ..dao import Database, ObjectNotFoundError, ObjectStorage

HERE = Path(__file__).parent.resolve()

CONFIG: Config = config


def process_message(message: dict):
    """Processes the message by checking if the file really is in the outbox,
    otherwise throwing an error"""

    # Check if file exists in database
    with Database() as database:
        db_object_info = database.get_drs_object(message["file_id"])

        # Check if file is in outbox
        with ObjectStorage(config=CONFIG) as storage:
            if storage.does_object_exist(
                config.s3_outbox_bucket_id, message["file_id"]
            ):

                # Update information, in case something has changed
                database.update_drs_object(db_object_info)
                return

            # Throw error, if the file does not exist in the outbox
            raise ObjectNotFoundError(
                object_id=message["file_id"],
                bucket_id=message["grouping_label"],
            )


def run():
    """Runs a subscribing process."""

    # read json schema:
    with open(
        HERE / "file_staged_for_download.json", "r", encoding="utf8"
    ) as schema_file:
        message_schema = json.load(schema_file)

    # create a topic object:
    topic = AmqpTopic(
        connection_params=pika.ConnectionParameters(host=config.host, port=config.port),
        topic_name="file_staged_for_download",
        service_name="drs3",
        json_schema=message_schema,
    )

    # subscribe:
    topic.subscribe_for_ever(exec_on_message=process_message)


if __name__ == "__main__":
    run()
