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

"""Fixtures that can be used in both unit and integration tests"""

from .config import DEFAULT_CONFIG, get_config  # noqa: F401
from .psql import psql_fixture  # noqa: F401
from .pubsub import amqp_fixture  # noqa: F401
from .s3 import s3_fixture  # noqa: F401
from .state import FILES  # noqa: F401
