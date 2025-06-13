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

"""Tests for the CloudWatch Metric Streams tool."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from awslabs.cloudwatch_mcp_server.tools.metric_streams.metric_streams_tool import MetricStreamsTool, MetricStreamsOperation


@pytest.fixture
def mock_context():
    """Create a mock MCP context."""
    context = MagicMock()
    context.error = AsyncMock()
    return context


@pytest.fixture
def mock_metric_stream_service():
    """Create a mock metric stream service."""
    service = MagicMock()
    service.delete_metric_stream = AsyncMock()
    service.get_metric_stream = AsyncMock()
    service.list_metric_streams = AsyncMock()
    service.put_metric_stream = AsyncMock()
    service.start_metric_streams = AsyncMock()
    service.stop_metric_streams = AsyncMock()
    return service


@pytest.fixture
def metric_streams_tool(mock_metric_stream_service):
    """Create a MetricStreamsTool with a mock metric stream service."""
    with patch('awslabs.cloudwatch_mcp_server.tools.metric_streams.metric_streams_tool.ClientFactory') as mock_factory:
        mock_factory.get_cloudwatch_client.return_value = MagicMock()
        tool = MetricStreamsTool(region_name='us-east-1')
        tool.metric_stream_service = mock_metric_stream_service
        return tool


def test_register():
    """Test MetricStreamsTool registration."""
    tool = MetricStreamsTool()
    mock_server = MagicMock()
    mock_tool_decorator = MagicMock()
    mock_server.tool.return_value = mock_tool_decorator
    
    tool.register(mock_server)
    
    mock_server.tool.assert_called_once_with(
        name='cloudwatch_metric_streams',
        description="""
            Comprehensive tool for working with CloudWatch Metric Streams. Supports:
            
            - Creating and updating metric streams
            - Listing and retrieving metric stream details
            - Starting and stopping metric streams
            - Deleting metric streams
            
            Use this tool to manage CloudWatch Metric Streams for real-time metrics delivery to destinations like Amazon S3.
            """
    )
    mock_tool_decorator.assert_called_once_with(tool.cloudwatch_metric_streams)


@pytest.mark.asyncio
async def test_delete_metric_stream(metric_streams_tool, mock_context, mock_metric_stream_service):
    """Test delete_metric_stream operation."""
    mock_metric_stream_service.delete_metric_stream.return_value = {"status": "Successfully deleted metric stream: test-stream"}
    
    result = await metric_streams_tool.cloudwatch_metric_streams(
        mock_context,
        operation=MetricStreamsOperation.DELETE_METRIC_STREAM,
        name="test-stream"
    )
    
    mock_metric_stream_service.delete_metric_stream.assert_called_once_with(
        name="test-stream"
    )
    assert result == {"status": "Successfully deleted metric stream: test-stream"}


@pytest.mark.asyncio
async def test_get_metric_stream(metric_streams_tool, mock_context, mock_metric_stream_service):
    """Test get_metric_stream operation."""
    mock_metric_stream_service.get_metric_stream.return_value = {
        "name": "test-stream",
        "state": "ACTIVE"
    }
    
    result = await metric_streams_tool.cloudwatch_metric_streams(
        mock_context,
        operation=MetricStreamsOperation.GET_METRIC_STREAM,
        name="test-stream"
    )
    
    mock_metric_stream_service.get_metric_stream.assert_called_once_with(
        name="test-stream"
    )
    assert result == {"name": "test-stream", "state": "ACTIVE"}


@pytest.mark.asyncio
async def test_list_metric_streams(metric_streams_tool, mock_context, mock_metric_stream_service):
    """Test list_metric_streams operation."""
    mock_metric_stream_service.list_metric_streams.return_value = {
        "entries": [{"name": "test-stream", "state": "ACTIVE"}],
        "nextToken": None
    }
    
    result = await metric_streams_tool.cloudwatch_metric_streams(
        mock_context,
        operation=MetricStreamsOperation.LIST_METRIC_STREAMS,
        max_results=10,
        next_token=None
    )
    
    mock_metric_stream_service.list_metric_streams.assert_called_once_with(
        max_results=10,
        next_token=None
    )
    assert result == {"entries": [{"name": "test-stream", "state": "ACTIVE"}], "nextToken": None}


@pytest.mark.asyncio
async def test_put_metric_stream(metric_streams_tool, mock_context, mock_metric_stream_service):
    """Test put_metric_stream operation."""
    mock_metric_stream_service.put_metric_stream.return_value = {
        "status": "Successfully created or updated metric stream: test-stream",
        "arn": "arn:aws:cloudwatch:us-east-1:123456789012:metric-stream/test-stream"
    }
    
    result = await metric_streams_tool.cloudwatch_metric_streams(
        mock_context,
        operation=MetricStreamsOperation.PUT_METRIC_STREAM,
        name="test-stream",
        firehose_arn="arn:aws:firehose:us-east-1:123456789012:deliverystream/test-stream",
        role_arn="arn:aws:iam::123456789012:role/test-role",
        output_format="json",
        include_filters=[{"Namespace": "AWS/EC2"}]
    )
    
    mock_metric_stream_service.put_metric_stream.assert_called_once_with(
        name="test-stream",
        firehose_arn="arn:aws:firehose:us-east-1:123456789012:deliverystream/test-stream",
        role_arn="arn:aws:iam::123456789012:role/test-role",
        output_format="json",
        include_filters=[{"Namespace": "AWS/EC2"}],
        exclude_filters=None,
        statistics_configurations=None,
        include_linked_accounts_metrics=None
    )
    assert result == {
        "status": "Successfully created or updated metric stream: test-stream",
        "arn": "arn:aws:cloudwatch:us-east-1:123456789012:metric-stream/test-stream"
    }