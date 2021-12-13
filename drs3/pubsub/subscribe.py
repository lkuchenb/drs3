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

from pathlib import Path

from ghga_service_chassis_lib.pubsub import AmqpTopic

from ..config import CONFIG, Config
from ..core import handle_staged_file
from . import schemas

HERE = Path(__file__).parent.resolve()


def process_file_staged_message(message: dict, config):
    """
    Processes the message by checking if the file really is in the outbox,
    otherwise throwing an error
    """

    handle_staged_file(message=message, config=config)


def subscribe_file_staged(config: Config = CONFIG, run_forever: bool = True) -> None:
    """
    Runs a subscribing process for the "file_staged_for_download topic"
    """

    # create a topic object:
    topic = AmqpTopic(
        config=config,
        topic_name=config.topic_name_file_staged,
        json_schema=schemas.FILE_STAGED,
    )

    # subscribe:
    topic.subscribe(
        exec_on_message=lambda message: process_file_staged_message(
            message, config=config
        ),
        run_forever=run_forever,
    )


if __name__ == "__main__":
    subscribe_file_staged()
