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

"""Tests for the CloudWatch OAM tool."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from awslabs.cloudwatch_mcp_server.tools.oam.oam_tool import OAMTool, OAMOperation


@pytest.fixture
def mock_context():
    """Create a mock MCP context."""
    context = MagicMock()
    context.error = AsyncMock()
    return context


@pytest.fixture
def mock_oam_service():
    """Create a mock OAM service."""
    service = MagicMock()
    service.list_sinks = AsyncMock()
    service.get_sink = AsyncMock()
    service.create_sink = AsyncMock()
    service.update_sink = AsyncMock()
    service.delete_sink = AsyncMock()
    service.list_links = AsyncMock()
    service.get_link = AsyncMock()
    service.create_link = AsyncMock()
    service.update_link = AsyncMock()
    service.delete_link = AsyncMock()
    service.list_attached_links = AsyncMock()
    return service


@pytest.fixture
def oam_tool(mock_oam_service):
    """Create an OAMTool with a mock OAM service."""
    with patch('awslabs.cloudwatch_mcp_server.tools.oam.oam_tool.ClientFactory') as mock_factory:
        mock_factory.get_oam_client.return_value = MagicMock()
        tool = OAMTool(region_name='us-east-1')
        tool.oam_service = mock_oam_service
        return tool


def test_register():
    """Test OAMTool registration."""
    tool = OAMTool()
    mock_server = MagicMock()
    mock_tool_decorator = MagicMock()
    mock_server.tool.return_value = mock_tool_decorator
    
    tool.register(mock_server)
    
    mock_server.tool.assert_called_once_with(
        name='cloudwatch_oam',
        description="""
            Comprehensive tool for working with CloudWatch Observability Access Manager (OAM). Supports:
            
            - Managing OAM sinks for monitoring accounts
            - Managing OAM links for source accounts
            - Listing and filtering sinks and links
            - Creating cross-account observability configurations
            
            Use this tool to set up and manage cross-account observability for CloudWatch metrics and logs.
            """
    )
    mock_tool_decorator.assert_called_once_with(tool.cloudwatch_oam)


@pytest.mark.asyncio
async def test_list_sinks(oam_tool, mock_context, mock_oam_service):
    """Test list_sinks operation."""
    mock_oam_service.list_sinks.return_value = {"Sinks": []}
    
    result = await oam_tool.cloudwatch_oam(
        mock_context,
        operation=OAMOperation.LIST_SINKS,
        max_results=10,
        next_token="token123"
    )
    
    mock_oam_service.list_sinks.assert_called_once_with(
        max_results=10,
        next_token="token123"
    )
    assert result == {"Sinks": []}


@pytest.mark.asyncio
async def test_get_sink(oam_tool, mock_context, mock_oam_service):
    """Test get_sink operation."""
    mock_oam_service.get_sink.return_value = {"Sink": {}}
    
    result = await oam_tool.cloudwatch_oam(
        mock_context,
        operation=OAMOperation.GET_SINK,
        sink_identifier="sink-123"
    )
    
    mock_oam_service.get_sink.assert_called_once_with(
        sink_identifier="sink-123"
    )
    assert result == {"Sink": {}}


@pytest.mark.asyncio
async def test_create_sink(oam_tool, mock_context, mock_oam_service):
    """Test create_sink operation."""
    mock_oam_service.create_sink.return_value = {"Sink": {}}
    
    result = await oam_tool.cloudwatch_oam(
        mock_context,
        operation=OAMOperation.CREATE_SINK,
        name="test-sink",
        alias="Test Sink",
        tags={"Environment": "Test"}
    )
    
    mock_oam_service.create_sink.assert_called_once_with(
        name="test-sink",
        alias="Test Sink",
        tags={"Environment": "Test"}
    )
    assert result == {"Sink": {}}


@pytest.mark.asyncio
async def test_list_links(oam_tool, mock_context, mock_oam_service):
    """Test list_links operation."""
    mock_oam_service.list_links.return_value = {"Links": []}
    
    result = await oam_tool.cloudwatch_oam(
        mock_context,
        operation=OAMOperation.LIST_LINKS,
        sink_identifier="sink-123",
        max_results=10,
        next_token="token123"
    )
    
    mock_oam_service.list_links.assert_called_once_with(
        sink_identifier="sink-123",
        max_results=10,
        next_token="token123"
    )
    assert result == {"Links": []}