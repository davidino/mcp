# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
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

"""CloudWatch Tag API routes."""

from typing import Dict, List
from mcp.server.fastmcp import Context
from pydantic import Field

from awslabs.cloudwatch_metrics_mcp_server.services.tag_service import TagService
from awslabs.cloudwatch_metrics_mcp_server.services.client_factory import ClientFactory


# Initialize services
cloudwatch_client = ClientFactory.get_cloudwatch_client()
tag_service = TagService(cloudwatch_client)


async def list_tags_for_resource_route(
    ctx: Context,
    mcp,
    resource_arn: str = Field(
        ...,
        description='The ARN of the CloudWatch resource.',
    ),
):
    """Route for list_tags_for_resource API."""
    return await tag_service.list_tags_for_resource(
        resource_arn=resource_arn,
    )


async def tag_resource_route(
    ctx: Context,
    mcp,
    resource_arn: str = Field(
        ...,
        description='The ARN of the CloudWatch resource.',
    ),
    tags: List[Dict[str, str]] = Field(
        ...,
        description='The list of tags to add to the resource. Each tag is a dictionary with "Key" and "Value" keys.',
    ),
):
    """Route for tag_resource API."""
    return await tag_service.tag_resource(
        resource_arn=resource_arn,
        tags=tags,
    )


async def untag_resource_route(
    ctx: Context,
    mcp,
    resource_arn: str = Field(
        ...,
        description='The ARN of the CloudWatch resource.',
    ),
    tag_keys: List[str] = Field(
        ...,
        description='The list of tag keys to remove from the resource.',
    ),
):
    """Route for untag_resource API."""
    return await tag_service.untag_resource(
        resource_arn=resource_arn,
        tag_keys=tag_keys,
    )


def register_routes(mcp_server):
    """Register all tag routes with the MCP server."""
    mcp_server.tool(name='list_tags_for_resource')(list_tags_for_resource_route)
    mcp_server.tool(name='tag_resource')(tag_resource_route)
    mcp_server.tool(name='untag_resource')(untag_resource_route)