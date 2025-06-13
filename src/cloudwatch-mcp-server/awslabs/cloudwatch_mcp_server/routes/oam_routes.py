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

"""CloudWatch OAM (Observability Access Manager) API routes."""

from typing import Dict, List, Optional, Any
from mcp.server.fastmcp import Context
from pydantic import Field
from mcp.types import ToolAnnotations

from awslabs.cloudwatch_mcp_server.services.oam_service import OAMService
from awslabs.cloudwatch_mcp_server.services.client_factory import ClientFactory


# Initialize services
oam_client = ClientFactory.get_oam_client()
oam_service = OAMService(oam_client)


async def list_sinks_route(
    ctx: Context,
    mcp,
    max_results: Optional[int] = Field(
        None,
        description='Maximum number of results to return',
    ),
    next_token: Optional[str] = Field(
        None,
        description='Token for pagination',
    ),
) -> Dict[str, Any]:
    """Lists OAM sinks in your AWS account.
    
    This tool retrieves information about available OAM sinks in your AWS account.
    
    Usage: Use this tool to discover available OAM sinks that you can use for cross-account observability.
    """
    return await oam_service.list_sinks(
        max_results=max_results,
        next_token=next_token,
    )


async def get_sink_route(
    ctx: Context,
    mcp,
    sink_identifier: str = Field(
        ...,
        description='The ARN or ID of the sink',
    ),
) -> Dict[str, Any]:
    """Gets details about a specific OAM sink.
    
    This tool retrieves detailed information about a specific OAM sink.
    
    Usage: Use this tool to get information about a specific OAM sink configuration.
    """
    return await oam_service.get_sink(
        sink_identifier=sink_identifier,
    )


async def create_sink_route(
    ctx: Context,
    mcp,
    name: str = Field(
        ...,
        description='The name of the sink',
    ),
    alias: Optional[str] = Field(
        None,
        description='Optional alias for the sink',
    ),
    tags: Optional[Dict[str, str]] = Field(
        None,
        description='Optional tags to apply to the sink',
    ),
) -> Dict[str, Any]:
    """Creates a new OAM sink in your AWS account.
    
    This tool creates a new OAM sink that can be used as a destination for cross-account observability data.
    
    Usage: Use this tool to create a new OAM sink in a monitoring account.
    """
    return await oam_service.create_sink(
        name=name,
        alias=alias,
        tags=tags,
    )


async def update_sink_route(
    ctx: Context,
    mcp,
    sink_identifier: str = Field(
        ...,
        description='The ARN or ID of the sink',
    ),
    alias: str = Field(
        ...,
        description='The new alias for the sink',
    ),
) -> Dict[str, Any]:
    """Updates an existing OAM sink.
    
    This tool updates the configuration of an existing OAM sink.
    
    Usage: Use this tool to modify the alias of an existing OAM sink.
    """
    return await oam_service.update_sink(
        sink_identifier=sink_identifier,
        alias=alias,
    )


async def delete_sink_route(
    ctx: Context,
    mcp,
    sink_identifier: str = Field(
        ...,
        description='The ARN or ID of the sink to delete',
    ),
) -> Dict[str, Any]:
    """Deletes an OAM sink.
    
    This tool deletes an OAM sink from your AWS account.
    
    Usage: Use this tool to remove an OAM sink that is no longer needed.
    """
    return await oam_service.delete_sink(
        sink_identifier=sink_identifier,
    )


async def list_links_route(
    ctx: Context,
    mcp,
    sink_identifier: Optional[str] = Field(
        None,
        description='Optional sink identifier to filter links',
    ),
    max_results: Optional[int] = Field(
        None,
        description='Maximum number of results to return',
    ),
    next_token: Optional[str] = Field(
        None,
        description='Token for pagination',
    ),
) -> Dict[str, Any]:
    """Lists OAM links in your AWS account.
    
    This tool retrieves information about available OAM links in your AWS account.
    You can filter the links by sink identifier.
    
    Usage: Use this tool to discover available OAM links that connect source accounts to monitoring accounts.
    """
    return await oam_service.list_links(
        sink_identifier=sink_identifier,
        max_results=max_results,
        next_token=next_token,
    )


async def get_link_route(
    ctx: Context,
    mcp,
    link_identifier: str = Field(
        ...,
        description='The ARN or ID of the link',
    ),
) -> Dict[str, Any]:
    """Gets details about a specific OAM link.
    
    This tool retrieves detailed information about a specific OAM link.
    
    Usage: Use this tool to get information about a specific OAM link configuration.
    """
    return await oam_service.get_link(
        link_identifier=link_identifier,
    )


async def create_link_route(
    ctx: Context,
    mcp,
    sink_identifier: str = Field(
        ...,
        description='The ARN or ID of the sink to link to',
    ),
    label: str = Field(
        ...,
        description='A label for the link',
    ),
    resource_types: List[str] = Field(
        ...,
        description='List of resource types to include in the link (e.g., ["METRICS", "LOGS"])',
    ),
    tags: Optional[Dict[str, str]] = Field(
        None,
        description='Optional tags to apply to the link',
    ),
) -> Dict[str, Any]:
    """Creates a new OAM link.
    
    This tool creates a new OAM link that connects a source account to a monitoring account sink.
    
    Usage: Use this tool to create a new OAM link in a source account to send observability data to a monitoring account.
    """
    return await oam_service.create_link(
        sink_identifier=sink_identifier,
        label=label,
        resource_types=resource_types,
        tags=tags,
    )


async def update_link_route(
    ctx: Context,
    mcp,
    link_identifier: str = Field(
        ...,
        description='The ARN or ID of the link',
    ),
    resource_types: List[str] = Field(
        ...,
        description='Updated list of resource types to include in the link',
    ),
) -> Dict[str, Any]:
    """Updates an existing OAM link.
    
    This tool updates the configuration of an existing OAM link.
    
    Usage: Use this tool to modify the resource types of an existing OAM link.
    """
    return await oam_service.update_link(
        link_identifier=link_identifier,
        resource_types=resource_types,
    )


async def delete_link_route(
    ctx: Context,
    mcp,
    link_identifier: str = Field(
        ...,
        description='The ARN or ID of the link to delete',
    ),
) -> Dict[str, Any]:
    """Deletes an OAM link.
    
    This tool deletes an OAM link from your AWS account.
    
    Usage: Use this tool to remove an OAM link that is no longer needed.
    """
    return await oam_service.delete_link(
        link_identifier=link_identifier,
    )


async def list_attached_links_route(
    ctx: Context,
    mcp,
    sink_identifier: str = Field(
        ...,
        description='The ARN or ID of the sink',
    ),
    max_results: Optional[int] = Field(
        None,
        description='Maximum number of results to return',
    ),
    next_token: Optional[str] = Field(
        None,
        description='Token for pagination',
    ),
) -> Dict[str, Any]:
    """Lists links attached to a specific OAM sink.
    
    This tool retrieves information about OAM links attached to a specific sink.
    
    Usage: Use this tool to discover which source accounts are linked to a monitoring account sink.
    """
    return await oam_service.list_attached_links(
        sink_identifier=sink_identifier,
        max_results=max_results,
        next_token=next_token,
    )


def register_routes(mcp_server):
    """Register all OAM routes with the MCP server."""
    mcp_server.tool(
        name='list_oam_sinks',
        description='Lists OAM sinks in your AWS account for cross-account observability.',
        annotations=ToolAnnotations(
            title='List OAM Sinks',
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False
        )
    )(list_sinks_route)
    
    mcp_server.tool(
        name='get_oam_sink',
        description='Gets details about a specific OAM sink.',
        annotations=ToolAnnotations(
            title='Get OAM Sink',
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False
        )
    )(get_sink_route)
    
    mcp_server.tool(
        name='create_oam_sink',
        description='Creates a new OAM sink in a monitoring account for cross-account observability.',
        annotations=ToolAnnotations(
            title='Create OAM Sink',
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False
        )
    )(create_sink_route)
    
    mcp_server.tool(
        name='update_oam_sink',
        description='Updates an existing OAM sink configuration.',
        annotations=ToolAnnotations(
            title='Update OAM Sink',
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False
        )
    )(update_sink_route)
    
    mcp_server.tool(
        name='delete_oam_sink',
        description='Deletes an OAM sink that is no longer needed.',
        annotations=ToolAnnotations(
            title='Delete OAM Sink',
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=True,
            openWorldHint=False
        )
    )(delete_sink_route)
    
    mcp_server.tool(
        name='list_oam_links',
        description='Lists OAM links that connect source accounts to monitoring accounts.',
        annotations=ToolAnnotations(
            title='List OAM Links',
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False
        )
    )(list_links_route)
    
    mcp_server.tool(
        name='get_oam_link',
        description='Gets detailed information about a specific OAM link.',
        annotations=ToolAnnotations(
            title='Get OAM Link',
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False
        )
    )(get_link_route)
    
    mcp_server.tool(
        name='create_oam_link',
        description='Creates a new OAM link in a source account to send observability data to a monitoring account.',
        annotations=ToolAnnotations(
            title='Create OAM Link',
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False
        )
    )(create_link_route)
    
    mcp_server.tool(
        name='update_oam_link',
        description='Updates an existing OAM link configuration.',
        annotations=ToolAnnotations(
            title='Update OAM Link',
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False
        )
    )(update_link_route)
    
    mcp_server.tool(
        name='delete_oam_link',
        description='Deletes an OAM link that is no longer needed.',
        annotations=ToolAnnotations(
            title='Delete OAM Link',
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=True,
            openWorldHint=False
        )
    )(delete_link_route)
    
    mcp_server.tool(
        name='list_attached_oam_links',
        description='Lists all links attached to a specific OAM sink to see which source accounts are connected.',
        annotations=ToolAnnotations(
            title='List Attached OAM Links',
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False
        )
    )(list_attached_links_route)