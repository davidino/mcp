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

"""Unit tests for the CloudWatch OAM routes."""

import pytest
from unittest.mock import MagicMock, patch
import asyncio

from awslabs.cloudwatch_mcp_server.routes import oam_routes
from awslabs.cloudwatch_mcp_server.services.oam_service import OAMService


@pytest.fixture
def mock_context():
    """Create a mock MCP context."""
    return MagicMock()


@pytest.fixture
def mock_mcp():
    """Create a mock MCP object."""
    return MagicMock()


@pytest.fixture
def mock_oam_service():
    """Create a mock OAM service."""
    with patch('awslabs.cloudwatch_mcp_server.routes.oam_routes.oam_service') as mock_service:
        yield mock_service


class TestOAMRoutes:
    """Tests for the OAM routes."""

    @pytest.mark.asyncio
    async def test_list_sinks_route(self, mock_context, mock_mcp, mock_oam_service):
        """Test list_sinks_route function."""
        
        future = asyncio.Future()
        future.set_result({
            'Sinks': [
                {
                    'Id': 'sink-1234567890abcdef0',
                    'Arn': 'arn:aws:oam:us-east-1:123456789012:sink/sink-1234567890abcdef0',
                    'Name': 'TestSink',
                    'Status': 'ACTIVE'
                }
            ]
        })
        
        # Setup mock response
        mock_oam_service.list_sinks.return_value = future
        
        # Call the route function
        result = await oam_routes.list_sinks_route(
            ctx=mock_context,
            mcp=mock_mcp,
            max_results=10,
            next_token='token-123'
        )
        
        # Verify the result
        assert 'Sinks' in result
        assert len(result['Sinks']) == 1
        assert result['Sinks'][0]['Id'] == 'sink-1234567890abcdef0'
        
        # Verify the service was called correctly
        mock_oam_service.list_sinks.assert_called_once_with(
            max_results=10,
            next_token='token-123'
        )

    @pytest.mark.asyncio
    async def test_get_sink_route(self, mock_context, mock_mcp, mock_oam_service):
        """Test get_sink_route function."""
        future = asyncio.Future()
        future.set_result({
            'Sink': {
                'Id': 'sink-1234567890abcdef0',
                'Arn': 'arn:aws:oam:us-east-1:123456789012:sink/sink-1234567890abcdef0',
                'Name': 'TestSink',
                'Status': 'ACTIVE'
            }
        })
            
        # Setup mock response
        mock_oam_service.get_sink.return_value = future
        
        # Call the route function
        result = await oam_routes.get_sink_route(
            ctx=mock_context,
            mcp=mock_mcp,
            sink_identifier='sink-1234567890abcdef0'
        )
        
        # Verify the result
        assert 'Sink' in result
        assert result['Sink']['Id'] == 'sink-1234567890abcdef0'
        
        # Verify the service was called correctly
        mock_oam_service.get_sink.assert_called_once_with(
            sink_identifier='sink-1234567890abcdef0'
        )

    @pytest.mark.asyncio
    async def test_list_links_route(self, mock_context, mock_mcp, mock_oam_service):
        """Test list_links_route function."""
        
        future = asyncio.Future()
        future.set_result({
            'Links': [
                {
                    'Id': 'link-1234567890abcdef0',
                    'Arn': 'arn:aws:oam:us-east-1:123456789012:link/link-1234567890abcdef0',
                    'Label': 'TestLink',
                    'SinkArn': 'arn:aws:oam:us-east-1:123456789012:sink/sink-1234567890abcdef0',
                    'Status': 'ACTIVE'
                }
            ]
        })
        
        # Setup mock response
        mock_oam_service.list_links.return_value = future
        
        # Call the route function
        result = await oam_routes.list_links_route(
            ctx=mock_context,
            mcp=mock_mcp,
            sink_identifier='sink-1234567890abcdef0',
            max_results=10,
            next_token='token-123'
        )
        
        # Verify the result
        assert 'Links' in result
        assert len(result['Links']) == 1
        assert result['Links'][0]['Id'] == 'link-1234567890abcdef0'
        
        # Verify the service was called correctly
        mock_oam_service.list_links.assert_called_once_with(
            sink_identifier='sink-1234567890abcdef0',
            max_results=10,
            next_token='token-123'
        )

    @pytest.mark.asyncio
    async def test_get_link_route(self, mock_context, mock_mcp, mock_oam_service):
        """Test get_link_route function."""
        future = asyncio.Future()
        future.set_result({
            'Link': {
                'Id': 'link-1234567890abcdef0',
                'Arn': 'arn:aws:oam:us-east-1:123456789012:link/link-1234567890abcdef0',
                'Label': 'TestLink',
                'SinkArn': 'arn:aws:oam:us-east-1:123456789012:sink/sink-1234567890abcdef0',
                'Status': 'ACTIVE'
            }
        })
        
        # Setup mock response
        mock_oam_service.get_link.return_value = future
        
        # Call the route function
        result = await oam_routes.get_link_route(
            ctx=mock_context,
            mcp=mock_mcp,
            link_identifier='link-1234567890abcdef0'
        )
        
        # Verify the result
        assert 'Link' in result
        assert result['Link']['Id'] == 'link-1234567890abcdef0'
        
        # Verify the service was called correctly
        mock_oam_service.get_link.assert_called_once_with(
            link_identifier='link-1234567890abcdef0'
        )

    @pytest.mark.asyncio
    async def test_list_attached_links_route(self, mock_context, mock_mcp, mock_oam_service):
        """Test list_attached_links_route function."""
        future = asyncio.Future()
        future.set_result({
            'Links': [
                {
                    'Id': 'link-1234567890abcdef0',
                    'Arn': 'arn:aws:oam:us-east-1:123456789012:link/link-1234567890abcdef0',
                    'Label': 'TestLink',
                    'ResourceTypes': ['METRICS', 'LOGS'],
                    'Status': 'ACTIVE'
                }
            ]
        })
        
        # Setup mock response
        mock_oam_service.list_attached_links.return_value = future
        
        # Call the route function
        result = await oam_routes.list_attached_links_route(
            ctx=mock_context,
            mcp=mock_mcp,
            sink_identifier='sink-1234567890abcdef0',
            max_results=10,
            next_token='token-123'
        )
        
        # Verify the result
        assert 'Links' in result
        assert len(result['Links']) == 1
        assert result['Links'][0]['Id'] == 'link-1234567890abcdef0'
        
        # Verify the service was called correctly
        mock_oam_service.list_attached_links.assert_called_once_with(
            sink_identifier='sink-1234567890abcdef0',
            max_results=10,
            next_token='token-123'
        )