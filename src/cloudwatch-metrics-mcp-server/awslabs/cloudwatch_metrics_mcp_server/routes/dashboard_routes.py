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

"""CloudWatch Dashboard API routes."""

from typing import Dict, List, Optional
from mcp.server.fastmcp import Context
from pydantic import Field

from awslabs.cloudwatch_metrics_mcp_server.services.dashboard_service import DashboardService
from awslabs.cloudwatch_metrics_mcp_server.services.client_factory import ClientFactory


# Initialize services
cloudwatch_client = ClientFactory.get_cloudwatch_client()
dashboard_service = DashboardService(cloudwatch_client)


async def delete_dashboards_route(
    ctx: Context,
    mcp,
    dashboard_names: List[str] = Field(
        ...,
        description='The names of the dashboards to delete.',
    ),
):
    """Route for delete_dashboards API."""
    return await dashboard_service.delete_dashboards(
        dashboard_names=dashboard_names,
    )


async def get_dashboard_route(
    ctx: Context,
    mcp,
    dashboard_name: str = Field(
        ...,
        description='The name of the dashboard to retrieve.',
    ),
):
    """Route for get_dashboard API."""
    return await dashboard_service.get_dashboard(
        dashboard_name=dashboard_name,
    )


async def list_dashboards_route(
    ctx: Context,
    mcp,
    dashboard_name_prefix: Optional[str] = Field(
        None,
        description='The prefix of the dashboard names to filter by.',
    ),
    next_token: Optional[str] = Field(
        None,
        description='The token for the next set of results.',
    ),
):
    """Route for list_dashboards API."""
    return await dashboard_service.list_dashboards(
        dashboard_name_prefix=dashboard_name_prefix,
        next_token=next_token,
    )


async def put_dashboard_route(
    ctx: Context,
    mcp,
    dashboard_name: str = Field(
        ...,
        description='The name of the dashboard.',
    ),
    dashboard_body: str = Field(
        ...,
        description='The detailed information about the dashboard in JSON format.',
    ),
):
    """Route for put_dashboard API."""
    return await dashboard_service.put_dashboard(
        dashboard_name=dashboard_name,
        dashboard_body=dashboard_body,
    )


def register_routes(mcp_server):
    """Register all dashboard routes with the MCP server."""
    mcp_server.tool(name='delete_dashboards')(delete_dashboards_route)
    mcp_server.tool(name='get_dashboard')(get_dashboard_route)
    mcp_server.tool(name='list_dashboards')(list_dashboards_route)
    mcp_server.tool(name='put_dashboard')(put_dashboard_route)