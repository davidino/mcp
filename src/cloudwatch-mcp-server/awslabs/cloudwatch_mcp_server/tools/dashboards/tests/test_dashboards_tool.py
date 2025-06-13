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

"""Tests for the CloudWatch Dashboards tool."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from awslabs.cloudwatch_mcp_server.tools.dashboards.dashboards_tool import DashboardsTool, DashboardsOperation


@pytest.fixture
def mock_context():
    """Create a mock MCP context."""
    context = MagicMock()
    context.error = AsyncMock()
    return context


@pytest.fixture
def mock_dashboard_service():
    """Create a mock dashboard service."""
    service = MagicMock()
    service.delete_dashboards = AsyncMock()
    service.get_dashboard = AsyncMock()
    service.list_dashboards = AsyncMock()
    service.put_dashboard = AsyncMock()
    return service


@pytest.fixture
def dashboards_tool(mock_dashboard_service):
    """Create a DashboardsTool with a mock dashboard service."""
    with patch('awslabs.cloudwatch_mcp_server.tools.dashboards.dashboards_tool.ClientFactory') as mock_factory:
        mock_factory.get_cloudwatch_client.return_value = MagicMock()
        tool = DashboardsTool(region_name='us-east-1')
        tool.dashboard_service = mock_dashboard_service
        return tool


def test_register():
    """Test DashboardsTool registration."""
    tool = DashboardsTool()
    mock_server = MagicMock()
    mock_tool_decorator = MagicMock()
    mock_server.tool.return_value = mock_tool_decorator
    
    tool.register(mock_server)
    
    mock_server.tool.assert_called_once_with(
        name='cloudwatch_dashboards',
        description="""
            Comprehensive tool for working with CloudWatch Dashboards. Supports:
            
            - Creating and updating dashboards
            - Retrieving dashboard details
            - Listing dashboards in your account
            - Deleting dashboards
            
            Use this tool to manage CloudWatch dashboards for visualizing your metrics and monitoring your AWS resources.
            """
    )
    mock_tool_decorator.assert_called_once_with(tool.cloudwatch_dashboards)


@pytest.mark.asyncio
async def test_delete_dashboards(dashboards_tool, mock_context, mock_dashboard_service):
    """Test delete_dashboards operation."""
    mock_dashboard_service.delete_dashboards.return_value = {"status": "Successfully deleted 2 dashboards"}
    
    result = await dashboards_tool.cloudwatch_dashboards(
        mock_context,
        operation=DashboardsOperation.DELETE_DASHBOARDS,
        dashboard_names=["dashboard1", "dashboard2"]
    )
    
    mock_dashboard_service.delete_dashboards.assert_called_once_with(
        dashboard_names=["dashboard1", "dashboard2"]
    )
    assert result == {"status": "Successfully deleted 2 dashboards"}


@pytest.mark.asyncio
async def test_get_dashboard(dashboards_tool, mock_context, mock_dashboard_service):
    """Test get_dashboard operation."""
    mock_dashboard_service.get_dashboard.return_value = {
        "dashboardName": "test-dashboard",
        "dashboardArn": "arn:aws:cloudwatch::123456789012:dashboard/test-dashboard",
        "dashboardBody": "{\"widgets\":[]}"
    }
    
    result = await dashboards_tool.cloudwatch_dashboards(
        mock_context,
        operation=DashboardsOperation.GET_DASHBOARD,
        dashboard_name="test-dashboard"
    )
    
    mock_dashboard_service.get_dashboard.assert_called_once_with(
        dashboard_name="test-dashboard"
    )
    assert result["dashboardName"] == "test-dashboard"
    assert "dashboardBody" in result


@pytest.mark.asyncio
async def test_list_dashboards(dashboards_tool, mock_context, mock_dashboard_service):
    """Test list_dashboards operation."""
    mock_dashboard_service.list_dashboards.return_value = {
        "dashboardEntries": [
            {
                "DashboardName": "test-dashboard",
                "DashboardArn": "arn:aws:cloudwatch::123456789012:dashboard/test-dashboard"
            }
        ],
        "nextToken": None
    }
    
    result = await dashboards_tool.cloudwatch_dashboards(
        mock_context,
        operation=DashboardsOperation.LIST_DASHBOARDS,
        dashboard_name_prefix="test",
        next_token=None
    )
    
    mock_dashboard_service.list_dashboards.assert_called_once_with(
        dashboard_name_prefix="test",
        next_token=None
    )
    assert "dashboardEntries" in result
    assert len(result["dashboardEntries"]) == 1
    assert result["dashboardEntries"][0]["DashboardName"] == "test-dashboard"


@pytest.mark.asyncio
async def test_put_dashboard(dashboards_tool, mock_context, mock_dashboard_service):
    """Test put_dashboard operation."""
    mock_dashboard_service.put_dashboard.return_value = {
        "dashboardValidationMessages": []
    }
    
    dashboard_body = {
        "widgets": [
            {
                "type": "metric",
                "x": 0,
                "y": 0,
                "width": 12,
                "height": 6,
                "properties": {
                    "metrics": [
                        ["AWS/EC2", "CPUUtilization", "InstanceId", "i-012345"]
                    ],
                    "period": 300,
                    "stat": "Average",
                    "region": "us-east-1",
                    "title": "EC2 Instance CPU"
                }
            }
        ]
    }
    
    result = await dashboards_tool.cloudwatch_dashboards(
        mock_context,
        operation=DashboardsOperation.PUT_DASHBOARD,
        dashboard_name="test-dashboard",
        dashboard_body=dashboard_body
    )
    
    mock_dashboard_service.put_dashboard.assert_called_once_with(
        dashboard_name="test-dashboard",
        dashboard_body=dashboard_body
    )
    assert "dashboardValidationMessages" in result