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

"""Test the messaging API (pubsub)"""

import uuid
from datetime import datetime

from drs3.models import DrsObjectInternal
from drs3.pubsub import publish_stage_request, schemas

from ..fixtures.config import get_config
from ..fixtures.pubsub import amqp_fixture  # noqa: F401
from ..fixtures.storage import EXISTING_OBJECTS


def test_publish_stage_request(amqp_fixture):  # noqa: F811
    """Test `subscribe_stage_requests` function"""

    config = get_config(sources=[amqp_fixture.config])

    drs_object = DrsObjectInternal(
        id=uuid.uuid4(),
        external_id=EXISTING_OBJECTS[0].object_id,
        registration_date=datetime.now(),
        md5_checksum=EXISTING_OBJECTS[0].md5,
        size=1000,
    )

    # initialize downstream test service that will receive
    # messages from this service:

    downstream_subscriber = amqp_fixture.get_test_subscriber(
        topic_name=config.topic_name_non_staged_file_requested,
        message_schema=schemas.NON_STAGED_FILE_REQUESTED,
    )

    # Call publish function

    publish_stage_request(drs_object=drs_object, config=config)

    # expect stage confirmation message:
    downstream_message = downstream_subscriber.subscribe(timeout_after=2)
    assert downstream_message["file_id"] == EXISTING_OBJECTS[0].object_id