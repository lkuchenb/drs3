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

""""Test core functionality"""

from typing import Optional, Type

import pytest

from drs3.core import get_drs_object_serve
from drs3.dao import DrsObjectNotFoundError

from ..fixtures import FILES, get_config, psql_fixture, s3_fixture  # noqa: F401

# call get_drs_object_serve with edge cases


@pytest.mark.parametrize(
    "file_name,expected_exception,expect_none",
    [
        ("in_registry_in_storage", None, False),
        ("in_registry_not_in_storage", None, True),
        ("not_in_registry_not_in_storage", DrsObjectNotFoundError, False),
    ],
)
def test_get_drs_object_serve(
    file_name: str,
    expected_exception: Optional[Type[BaseException]],
    psql_fixture,  # noqa: F811
    s3_fixture,  # noqa: F811
):
    """Test the response for a file request"""

    # get config
    config = get_config(sources=[psql_fixture.config, s3_fixture.config])

    file = FILES[file_name]

    # drs_id: str,
    # make_stage_request: Callable[[dict, Config], None],
    # config: Config = CONFIG,

    run = lambda: get_drs_object_serve(
        drs_id=file.file_id, make_stage_request=dummy_function, config=config
    )

    if expected_exception is None:
        run()
        assert s3_fixture.storage.does_object_exist(
            object_id=file.id,
            bucket_id=config.s3_outbox_bucket_id,
        )
    else:
        with pytest.raises(expected_exception):
            run()


def dummy_function(drs_object, config):
    pass
