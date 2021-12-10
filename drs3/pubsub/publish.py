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
Publish asynchronous topics
"""

import json
from pathlib import Path

from ghga_service_chassis_lib.pubsub import AmqpTopic

from .. import models
from ..config import Config, CONFIG
from . import schemas

HERE = Path(__file__).parent.resolve()


def publish_stage_request(drs_object: models.DrsObjectInternal, config: Config = CONFIG):
    """
    Publishes a message to a specified topic
    """

    topic_name = config.topic_name_stage_request


    message = {
        "request_id": "",
        "file_id": drs_object.file_id,
        "timestamp": drs_object.registration_date.isoformat(),
    }

    # create a topic object:
    topic = AmqpTopic(
        config=config,
        topic_name=topic_name,
        json_schema=schemas.STAGE_REQUEST,
    )

    topic.publish(message)
