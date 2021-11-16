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

"""Config Parameter Modeling and Parsing"""

from functools import lru_cache
from typing import List, Literal, Optional

from ghga_service_chassis_lib.config import config_from_yaml
from ghga_service_chassis_lib.pubsub import PubSubConfigBase

LogLevel = Literal["critical", "error", "warning", "info", "debug", "trace"]


@config_from_yaml(prefix="drs3")
class Config(PubSubConfigBase):
    """Config parameters and their defaults."""

    # config parameter needed for rabbitmq server
    # are inherited from PubSubConfigBase;

    # config parameter needed for drs3
    host: str = "127.0.0.1"
    port: int = 8080
    log_level: LogLevel = "info"
    auto_reload: bool = False
    workers: int = 1

    api_route: str = "/ga4gh/drs/v1"
    custom_spec_url: Optional[str] = None
    rabbitmq_host: str = "rabbitmq"
    rabbitmq_port: int = 5672
    topic_name_download_requested: str = "download_request"
    db_url: str = "postgresql://admin:admin@postgresql/storage"
    s3_url: str = "http://s3-localstack:4566"
    drs_self_url: str = "drs://localhost:8080/"

    cors_allowed_origins: List[str] = []
    cors_allow_credentials: bool = False
    cors_allowed_methods: List[str] = []
    cors_allowed_headers: List[str] = []


@lru_cache
def get_config():
    """Get runtime configuration."""
    return Config()
