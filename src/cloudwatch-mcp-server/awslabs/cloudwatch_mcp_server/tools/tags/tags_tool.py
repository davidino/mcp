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

"""CloudWatch Tags tool implementation."""

from enum import Enum
from typing import Dict, List, Any
from loguru import logger
from mcp.server.fastmcp import Context

from awslabs.cloudwatch_mcp_server.services.tag_service import TagService
from awslabs.cloudwatch_mcp_server.services.client_factory import ClientFactory


class TagsOperation(str, Enum):
    """Enum for CloudWatch Tags operations."""
    LIST_TAGS_FOR_RESOURCE = "list_tags_for_resource"
    TAG_RESOURCE = "tag_resource"
    UNTAG_RESOURCE = "untag_resource"


class TagsTool:
    """Tool for working with CloudWatch Tags."""
    
    def __init__(self, region_name: str = "us-east-1"):
        """Initialize the CloudWatch Tags tool.
        
        Args:
            region_name: AWS region name.
        """
        self.region_name = region_name
        cloudwatch_client = ClientFactory.get_cloudwatch_client(region_name=region_name)
        self.tag_service = TagService(cloudwatch_client)
    
    async def cloudwatch_tags(
        self,
        ctx: Context,
        operation: TagsOperation,
        resource_arn: str,
        tags: List[Dict[str, str]] = None,
        tag_keys: List[str] = None,
    ) -> Dict[str, Any]:
        """Perform CloudWatch Tags operations.
        
        Args:
            ctx: The MCP context.
            operation: The operation to perform.
            resource_arn: The ARN of the CloudWatch resource.
            tags: The list of tags to add to the resource.
            tag_keys: The list of tag keys to remove from the resource.
            
        Returns:
            The result of the operation, which varies based on the operation type.
        """
        try:
            if operation == TagsOperation.LIST_TAGS_FOR_RESOURCE:
                return await self._list_tags_for_resource(
                    ctx,
                    resource_arn=resource_arn,
                )
            if operation == TagsOperation.TAG_RESOURCE:
                if not tags:
                    raise ValueError("tags is required for tag_resource operation")
                
                return await self._tag_resource(
                    ctx,
                    resource_arn=resource_arn,
                    tags=tags,
                )
            if operation == TagsOperation.UNTAG_RESOURCE:
                if not tag_keys:
                    raise ValueError("tag_keys is required for untag_resource operation")
                
                return await self._untag_resource(
                    ctx,
                    resource_arn=resource_arn,
                    tag_keys=tag_keys,
                )
            else:
                raise ValueError(f"Unsupported operation: {operation}")
        except Exception as e:
            logger.error(f"Error in cloudwatch_tags tool: {str(e)}")
            await ctx.error(f"CloudWatch Tags operation failed: {str(e)}")
            raise
    
    async def _list_tags_for_resource(
        self,
        ctx: Context,
        resource_arn: str,
    ) -> Dict[str, Any]:
        """Lists the tags for a CloudWatch resource."""
        try:
            return await self.tag_service.list_tags_for_resource(
                resource_arn=resource_arn,
            )
        except Exception as e:
            logger.error(f"Error in list_tags_for_resource: {str(e)}")
            await ctx.error(f"Failed to list tags for resource: {str(e)}")
            raise
    
    async def _tag_resource(
        self,
        ctx: Context,
        resource_arn: str,
        tags: List[Dict[str, str]],
    ) -> Dict[str, str]:
        """Adds or modifies tags for a CloudWatch resource."""
        try:
            return await self.tag_service.tag_resource(
                resource_arn=resource_arn,
                tags=tags,
            )
        except Exception as e:
            logger.error(f"Error in tag_resource: {str(e)}")
            await ctx.error(f"Failed to tag resource: {str(e)}")
            raise
    
    async def _untag_resource(
        self,
        ctx: Context,
        resource_arn: str,
        tag_keys: List[str],
    ) -> Dict[str, str]:
        """Removes tags from a CloudWatch resource."""
        try:
            return await self.tag_service.untag_resource(
                resource_arn=resource_arn,
                tag_keys=tag_keys,
            )
        except Exception as e:
            logger.error(f"Error in untag_resource: {str(e)}")
            await ctx.error(f"Failed to untag resource: {str(e)}")
            raise
    
    def register(self, mcp_server):
        """Register the CloudWatch Tags tool with the MCP server.
        
        Args:
            mcp_server: The MCP server to register the tool with.
        """
        mcp_server.tool(
            name='cloudwatch_tags',
            description="""
            Tool for working with CloudWatch resource tags. Supports:
            
            - Listing tags for CloudWatch resources
            - Adding or modifying tags for resources
            - Removing tags from resources
            
            Use this tool to manage tags for your CloudWatch resources.
            """
        )(self.cloudwatch_tags)