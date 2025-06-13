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

"""CloudWatch Dashboards tool implementation."""

from enum import Enum
from typing import Dict, List, Optional, Any, Union
from loguru import logger
from mcp.server.fastmcp import Context

from awslabs.cloudwatch_mcp_server.services.dashboard_service import DashboardService
from awslabs.cloudwatch_mcp_server.services.client_factory import ClientFactory


class DashboardsOperation(str, Enum):
    """Enum for CloudWatch Dashboards operations."""
    DELETE_DASHBOARDS = "delete_dashboards"
    GET_DASHBOARD = "get_dashboard"
    LIST_DASHBOARDS = "list_dashboards"
    PUT_DASHBOARD = "put_dashboard"


class DashboardsTool:
    """Tool for working with CloudWatch Dashboards."""
    
    def __init__(self, region_name: str = "us-east-1"):
        """Initialize the CloudWatch Dashboards tool.
        
        Args:
            region_name: AWS region name.
        """
        self.region_name = region_name
        cloudwatch_client = ClientFactory.get_cloudwatch_client(region_name=region_name)
        self.dashboard_service = DashboardService(cloudwatch_client)
    
    async def cloudwatch_dashboards(
        self,
        ctx: Context,
        operation: DashboardsOperation,
        # Parameters for dashboard operations
        dashboard_name: Optional[str] = None,
        dashboard_names: Optional[List[str]] = None,
        dashboard_name_prefix: Optional[str] = None,
        dashboard_body: Optional[Union[str, Dict[str, Any]]] = None,
        # Pagination parameters
        next_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Perform CloudWatch Dashboards operations.
        
        Args:
            ctx: The MCP context.
            operation: The operation to perform.
            
            # Parameters for dashboard operations
            dashboard_name: The name of the dashboard.
            dashboard_names: The names of the dashboards (for delete operation).
            dashboard_name_prefix: The prefix for filtering dashboards.
            dashboard_body: The dashboard body as a string or dictionary.
            
            # Pagination parameters
            next_token: Token for pagination.
            
        Returns:
            The result of the operation, which varies based on the operation type.
        """
        try:
            if operation == DashboardsOperation.DELETE_DASHBOARDS:
                if not dashboard_names:
                    raise ValueError("dashboard_names is required for delete_dashboards operation")
                
                return await self._delete_dashboards(
                    ctx,
                    dashboard_names=dashboard_names,
                )
            elif operation == DashboardsOperation.GET_DASHBOARD:
                if not dashboard_name:
                    raise ValueError("dashboard_name is required for get_dashboard operation")
                
                return await self._get_dashboard(
                    ctx,
                    dashboard_name=dashboard_name,
                )
            elif operation == DashboardsOperation.LIST_DASHBOARDS:
                return await self._list_dashboards(
                    ctx,
                    dashboard_name_prefix=dashboard_name_prefix,
                    next_token=next_token,
                )
            elif operation == DashboardsOperation.PUT_DASHBOARD:
                if not dashboard_name or dashboard_body is None:
                    raise ValueError("dashboard_name and dashboard_body are required for put_dashboard operation")
                
                return await self._put_dashboard(
                    ctx,
                    dashboard_name=dashboard_name,
                    dashboard_body=dashboard_body,
                )
            else:
                raise ValueError(f"Unsupported operation: {operation}")
        except Exception as e:
            logger.error(f"Error in cloudwatch_dashboards tool: {str(e)}")
            await ctx.error(f"CloudWatch Dashboards operation failed: {str(e)}")
            raise
    
    async def _delete_dashboards(
        self,
        ctx: Context,
        dashboard_names: List[str],
    ) -> Dict[str, str]:
        """Deletes the specified CloudWatch dashboards."""
        try:
            return await self.dashboard_service.delete_dashboards(
                dashboard_names=dashboard_names,
            )
        except Exception as e:
            logger.error(f"Error in delete_dashboards: {str(e)}")
            await ctx.error(f"Failed to delete dashboards: {str(e)}")
            raise
    
    async def _get_dashboard(
        self,
        ctx: Context,
        dashboard_name: str,
    ) -> Dict[str, Any]:
        """Gets details about a specific CloudWatch dashboard."""
        try:
            return await self.dashboard_service.get_dashboard(
                dashboard_name=dashboard_name,
            )
        except Exception as e:
            logger.error(f"Error in get_dashboard: {str(e)}")
            await ctx.error(f"Failed to get dashboard: {str(e)}")
            raise
    
    async def _list_dashboards(
        self,
        ctx: Context,
        dashboard_name_prefix: Optional[str] = None,
        next_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Lists CloudWatch dashboards in your AWS account."""
        try:
            return await self.dashboard_service.list_dashboards(
                dashboard_name_prefix=dashboard_name_prefix,
                next_token=next_token,
            )
        except Exception as e:
            logger.error(f"Error in list_dashboards: {str(e)}")
            await ctx.error(f"Failed to list dashboards: {str(e)}")
            raise
    
    async def _put_dashboard(
        self,
        ctx: Context,
        dashboard_name: str,
        dashboard_body: Union[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Creates or updates a CloudWatch dashboard."""
        try:
            return await self.dashboard_service.put_dashboard(
                dashboard_name=dashboard_name,
                dashboard_body=dashboard_body,
            )
        except Exception as e:
            logger.error(f"Error in put_dashboard: {str(e)}")
            await ctx.error(f"Failed to put dashboard: {str(e)}")
            raise
    
    def register(self, mcp_server):
        """Register the CloudWatch Dashboards tool with the MCP server.
        
        Args:
            mcp_server: The MCP server to register the tool with.
        """
        mcp_server.tool(
            name='cloudwatch_dashboards',
            description="""
            Comprehensive tool for working with CloudWatch Dashboards. Supports:
            
            - Creating and updating dashboards
            - Retrieving dashboard details
            - Listing dashboards in your account
            - Deleting dashboards
            
            Use this tool to manage CloudWatch dashboards for visualizing your metrics and monitoring your AWS resources.
            """
        )(self.cloudwatch_dashboards)