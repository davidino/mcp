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

"""CloudWatch OAM (Observability Access Manager) tool implementation."""

from enum import Enum
from typing import Dict, List, Optional, Any
from loguru import logger
from mcp.server.fastmcp import Context

from awslabs.cloudwatch_mcp_server.services.oam_service import OAMService
from awslabs.cloudwatch_mcp_server.services.client_factory import ClientFactory


class OAMOperation(str, Enum):
    """Enum for CloudWatch OAM operations."""
    LIST_SINKS = "list_sinks"
    GET_SINK = "get_sink"
    CREATE_SINK = "create_sink"
    UPDATE_SINK = "update_sink"
    DELETE_SINK = "delete_sink"
    LIST_LINKS = "list_links"
    GET_LINK = "get_link"
    CREATE_LINK = "create_link"
    UPDATE_LINK = "update_link"
    DELETE_LINK = "delete_link"
    LIST_ATTACHED_LINKS = "list_attached_links"


class OAMTool:
    """Tool for working with CloudWatch OAM (Observability Access Manager)."""
    
    def __init__(self, region_name: str = "us-east-1"):
        """Initialize the CloudWatch OAM tool.
        
        Args:
            region_name: AWS region name.
        """
        self.region_name = region_name
        oam_client = ClientFactory.get_oam_client(region_name=region_name)
        self.oam_service = OAMService(oam_client)
    
    async def cloudwatch_oam(
        self,
        ctx: Context,
        operation: OAMOperation,
        # Parameters for sink operations
        sink_identifier: Optional[str] = None,
        name: Optional[str] = None,
        alias: Optional[str] = None,
        # Parameters for link operations
        link_identifier: Optional[str] = None,
        label: Optional[str] = None,
        resource_types: Optional[List[str]] = None,
        # Common parameters
        tags: Optional[Dict[str, str]] = None,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Perform CloudWatch OAM operations.
        
        Args:
            ctx: The MCP context.
            operation: The operation to perform.
            
            # Parameters for sink operations
            sink_identifier: The ARN or ID of the sink.
            name: The name of the sink for create operations.
            alias: The alias for the sink.
            
            # Parameters for link operations
            link_identifier: The ARN or ID of the link.
            label: A label for the link.
            resource_types: List of resource types to include in the link.
            
            # Common parameters
            tags: Tags to apply to the resource.
            max_results: Maximum number of results to return.
            next_token: Token for pagination.
            
        Returns:
            The result of the operation, which varies based on the operation type.
        """
        try:
            if operation == OAMOperation.LIST_SINKS:
                return await self._list_sinks(
                    ctx,
                    max_results=max_results,
                    next_token=next_token,
                )
            if operation == OAMOperation.GET_SINK:
                if not sink_identifier:
                    raise ValueError("sink_identifier is required for get_sink operation")
                
                return await self._get_sink(
                    ctx,
                    sink_identifier=sink_identifier,
                )
            if operation == OAMOperation.CREATE_SINK:
                if not name:
                    raise ValueError("name is required for create_sink operation")
                
                return await self._create_sink(
                    ctx,
                    name=name,
                    alias=alias,
                    tags=tags,
                )
            if operation == OAMOperation.UPDATE_SINK:
                if not sink_identifier or not alias:
                    raise ValueError("sink_identifier and alias are required for update_sink operation")
                
                return await self._update_sink(
                    ctx,
                    sink_identifier=sink_identifier,
                    alias=alias,
                )
            if operation == OAMOperation.DELETE_SINK:
                if not sink_identifier:
                    raise ValueError("sink_identifier is required for delete_sink operation")
                
                return await self._delete_sink(
                    ctx,
                    sink_identifier=sink_identifier,
                )
            if operation == OAMOperation.LIST_LINKS:
                return await self._list_links(
                    ctx,
                    sink_identifier=sink_identifier,
                    max_results=max_results,
                    next_token=next_token,
                )
            if operation == OAMOperation.GET_LINK:
                if not link_identifier:
                    raise ValueError("link_identifier is required for get_link operation")
                
                return await self._get_link(
                    ctx,
                    link_identifier=link_identifier,
                )
            if operation == OAMOperation.CREATE_LINK:
                if not sink_identifier or not label or not resource_types:
                    raise ValueError("sink_identifier, label, and resource_types are required for create_link operation")
                
                return await self._create_link(
                    ctx,
                    sink_identifier=sink_identifier,
                    label=label,
                    resource_types=resource_types,
                    tags=tags,
                )
            if operation == OAMOperation.UPDATE_LINK:
                if not link_identifier or not resource_types:
                    raise ValueError("link_identifier and resource_types are required for update_link operation")
                
                return await self._update_link(
                    ctx,
                    link_identifier=link_identifier,
                    resource_types=resource_types,
                )
            if operation == OAMOperation.DELETE_LINK:
                if not link_identifier:
                    raise ValueError("link_identifier is required for delete_link operation")
                
                return await self._delete_link(
                    ctx,
                    link_identifier=link_identifier,
                )
            if operation == OAMOperation.LIST_ATTACHED_LINKS:
                if not sink_identifier:
                    raise ValueError("sink_identifier is required for list_attached_links operation")
                
                return await self._list_attached_links(
                    ctx,
                    sink_identifier=sink_identifier,
                    max_results=max_results,
                    next_token=next_token,
                )
            else:
                raise ValueError(f"Unsupported operation: {operation}")
        except Exception as e:
            logger.error(f"Error in cloudwatch_oam tool: {str(e)}")
            await ctx.error(f"CloudWatch OAM operation failed: {str(e)}")
            raise
    
    async def _list_sinks(
        self,
        ctx: Context,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Lists OAM sinks in your AWS account."""
        try:
            return await self.oam_service.list_sinks(
                max_results=max_results,
                next_token=next_token,
            )
        except Exception as e:
            logger.error(f"Error in list_sinks: {str(e)}")
            await ctx.error(f"Failed to list sinks: {str(e)}")
            raise
    
    async def _get_sink(
        self,
        ctx: Context,
        sink_identifier: str,
    ) -> Dict[str, Any]:
        """Gets details about a specific OAM sink."""
        try:
            return await self.oam_service.get_sink(
                sink_identifier=sink_identifier,
            )
        except Exception as e:
            logger.error(f"Error in get_sink: {str(e)}")
            await ctx.error(f"Failed to get sink: {str(e)}")
            raise
    
    async def _create_sink(
        self,
        ctx: Context,
        name: str,
        alias: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Creates a new OAM sink."""
        try:
            return await self.oam_service.create_sink(
                name=name,
                alias=alias,
                tags=tags,
            )
        except Exception as e:
            logger.error(f"Error in create_sink: {str(e)}")
            await ctx.error(f"Failed to create sink: {str(e)}")
            raise
    
    async def _update_sink(
        self,
        ctx: Context,
        sink_identifier: str,
        alias: str,
    ) -> Dict[str, Any]:
        """Updates an existing OAM sink."""
        try:
            return await self.oam_service.update_sink(
                sink_identifier=sink_identifier,
                alias=alias,
            )
        except Exception as e:
            logger.error(f"Error in update_sink: {str(e)}")
            await ctx.error(f"Failed to update sink: {str(e)}")
            raise
    
    async def _delete_sink(
        self,
        ctx: Context,
        sink_identifier: str,
    ) -> Dict[str, Any]:
        """Deletes an OAM sink."""
        try:
            return await self.oam_service.delete_sink(
                sink_identifier=sink_identifier,
            )
        except Exception as e:
            logger.error(f"Error in delete_sink: {str(e)}")
            await ctx.error(f"Failed to delete sink: {str(e)}")
            raise
    
    async def _list_links(
        self,
        ctx: Context,
        sink_identifier: Optional[str] = None,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Lists OAM links in your AWS account."""
        try:
            return await self.oam_service.list_links(
                sink_identifier=sink_identifier,
                max_results=max_results,
                next_token=next_token,
            )
        except Exception as e:
            logger.error(f"Error in list_links: {str(e)}")
            await ctx.error(f"Failed to list links: {str(e)}")
            raise
    
    async def _get_link(
        self,
        ctx: Context,
        link_identifier: str,
    ) -> Dict[str, Any]:
        """Gets details about a specific OAM link."""
        try:
            return await self.oam_service.get_link(
                link_identifier=link_identifier,
            )
        except Exception as e:
            logger.error(f"Error in get_link: {str(e)}")
            await ctx.error(f"Failed to get link: {str(e)}")
            raise
    
    async def _create_link(
        self,
        ctx: Context,
        sink_identifier: str,
        label: str,
        resource_types: List[str],
        tags: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Creates a new OAM link."""
        try:
            return await self.oam_service.create_link(
                sink_identifier=sink_identifier,
                label=label,
                resource_types=resource_types,
                tags=tags,
            )
        except Exception as e:
            logger.error(f"Error in create_link: {str(e)}")
            await ctx.error(f"Failed to create link: {str(e)}")
            raise
    
    async def _update_link(
        self,
        ctx: Context,
        link_identifier: str,
        resource_types: List[str],
    ) -> Dict[str, Any]:
        """Updates an existing OAM link."""
        try:
            return await self.oam_service.update_link(
                link_identifier=link_identifier,
                resource_types=resource_types,
            )
        except Exception as e:
            logger.error(f"Error in update_link: {str(e)}")
            await ctx.error(f"Failed to update link: {str(e)}")
            raise
    
    async def _delete_link(
        self,
        ctx: Context,
        link_identifier: str,
    ) -> Dict[str, Any]:
        """Deletes an OAM link."""
        try:
            return await self.oam_service.delete_link(
                link_identifier=link_identifier,
            )
        except Exception as e:
            logger.error(f"Error in delete_link: {str(e)}")
            await ctx.error(f"Failed to delete link: {str(e)}")
            raise
    
    async def _list_attached_links(
        self,
        ctx: Context,
        sink_identifier: str,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Lists links attached to a specific OAM sink."""
        try:
            return await self.oam_service.list_attached_links(
                sink_identifier=sink_identifier,
                max_results=max_results,
                next_token=next_token,
            )
        except Exception as e:
            logger.error(f"Error in list_attached_links: {str(e)}")
            await ctx.error(f"Failed to list attached links: {str(e)}")
            raise
    
    def register(self, mcp_server):
        """Register the CloudWatch OAM tool with the MCP server.
        
        Args:
            mcp_server: The MCP server to register the tool with.
        """
        mcp_server.tool(
            name='cloudwatch_oam',
            description="""
            Comprehensive tool for working with CloudWatch Observability Access Manager (OAM). Supports:
            
            - Managing OAM sinks for monitoring accounts
            - Managing OAM links for source accounts
            - Listing and filtering sinks and links
            - Creating cross-account observability configurations
            
            Use this tool to set up and manage cross-account observability for CloudWatch metrics and logs.
            """
        )(self.cloudwatch_oam)