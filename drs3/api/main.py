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
Module containing the main API router and (optionally) top-level API enpoints.
Additional endpoints might be structured in dedicated modules
(each of them having a sub-router).
"""


from pathlib import Path
from typing import Any

from pyramid.config import Configurator
from pyramid.events import NewRequest
from pyramid.request import Request
from pyramid.view import view_config

from ..config import Config, config
from ..custom_openapi3.custom_explorer_view import add_custom_explorer_view
from ..models import DrsObjectServe
from .cors import cors_header_response_callback_factory


def get_app(config_: Config = config) -> Any:
    """
    Builds the Pyramid app
    Args:
        config_: Settings for the application
    Returns:
        An instance of Pyramid WSGI app
    """
    api_route = Path(config_.api_route)
    openapi_spec_path = Path(__file__).parent / "openapi.yaml"
    with Configurator() as pyramid_config:
        pyramid_config.add_directive(
            "pyramid_custom_openapi3_add_explorer", add_custom_explorer_view
        )

        pyramid_config.add_subscriber(
            cors_header_response_callback_factory(config_), NewRequest
        )

        pyramid_config.include("pyramid_openapi3")
        pyramid_config.pyramid_openapi3_spec(
            openapi_spec_path, route=str(api_route / "openapi.yaml")
        )
        pyramid_config.pyramid_custom_openapi3_add_explorer(
            route=str(api_route), custom_spec_url=config_.custom_spec_url
        )

        pyramid_config.add_route("hello", "/")
        pyramid_config.add_route("health", "/health")

        pyramid_config.add_route(
            "objects_id", str(api_route / "objects" / "{object_id}")
        )
        pyramid_config.add_route(
            "objects_id_access_id",
            str(api_route / "objects" / "{object_id}" / "access" / "{access_id}"),
        )
        pyramid_config.scan(".")
    return pyramid_config.make_wsgi_app()


@view_config(route_name="hello", renderer="json", openapi=False, request_method="GET")
def index(_, __):
    """
    Index Enpoint, returns 'Hello World'
    """
    return {"content": "Hello World!"}


@view_config(
    route_name="objects_id", renderer="json", openapi=True, request_method="GET"
)
def get_objects_id(
    request: Request,  # pylint: disable=unused-argument
) -> DrsObjectServe:
    """
    Get info about a ``DrsObject``.
    Args:
        request: An instance of ``pyramid.request.Request``
    Returns:
        An instance of ``DrsReturnObject``
    """
    ...


@view_config(route_name="health", renderer="json", openapi=False, request_method="GET")
def get_health(_, __):
    """
    Check for the health of the service.
    """
    return {"status": "OK"}
