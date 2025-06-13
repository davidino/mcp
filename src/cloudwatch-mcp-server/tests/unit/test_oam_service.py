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

"""Unit tests for the CloudWatch OAM service."""

import pytest
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError

from awslabs.cloudwatch_mcp_server.services.oam_service import OAMService

@pytest.fixture
def mock_oam_client():
    """Create a mock OAM client."""
    mock_client = MagicMock()
    return mock_client


@pytest.fixture
def oam_service(mock_oam_client):
    """Create an OAMService instance with a mock client."""
    return OAMService(mock_oam_client)


class TestOAMService:
    """Tests for the OAMService class."""

    @pytest.mark.asyncio
    async def test_list_sinks_success(self, oam_service, mock_oam_client):
        """Test successful list_sinks call."""
        # Setup mock response
        mock_oam_client.list_sinks.return_value = {
            'Sinks': [
                {
                    'Id': 'sink-1234567890abcdef0',
                    'Arn': 'arn:aws:oam:us-east-1:123456789012:sink/sink-1234567890abcdef0',
                    'Name': 'TestSink',
                    'Status': 'ACTIVE'
                }
            ],
            'NextToken': None
        }
        
        # Call the service method
        result = await oam_service.list_sinks(max_results=10, next_token=None)
        
        # Verify the result
        assert len(result['Sinks']) == 1
        assert result['Sinks'][0]['Id'] == 'sink-1234567890abcdef0'
        assert result['Sinks'][0]['Name'] == 'TestSink'
        
        # Verify the client was called correctly
        mock_oam_client.list_sinks.assert_called_once_with(MaxResults=10)

    @pytest.mark.asyncio
    async def test_list_sinks_with_pagination(self, oam_service, mock_oam_client):
        """Test list_sinks with pagination."""
        # Setup mock response
        mock_oam_client.list_sinks.return_value = {
            'Sinks': [
                {
                    'Id': 'sink-1234567890abcdef0',
                    'Arn': 'arn:aws:oam:us-east-1:123456789012:sink/sink-1234567890abcdef0',
                    'Name': 'TestSink',
                    'Status': 'ACTIVE'
                }
            ],
            'NextToken': 'next-token-value'
        }
        
        # Call the service method
        result = await oam_service.list_sinks(next_token='token-123')
        
        # Verify the result
        assert 'NextToken' in result
        assert result['NextToken'] == 'next-token-value'
        
        # Verify the client was called correctly
        mock_oam_client.list_sinks.assert_called_once_with(NextToken='token-123')

    @pytest.mark.asyncio
    async def test_list_sinks_error(self, oam_service, mock_oam_client):
        """Test list_sinks with ClientError."""
        # Setup mock to raise ClientError
        mock_oam_client.list_sinks.side_effect = ClientError(
            {'Error': {'Code': 'InvalidParameterValue', 'Message': 'Test error'}},
            'ListSinks'
        )
        
        # Call the service method and expect exception
        with pytest.raises(ClientError):
            await oam_service.list_sinks()

    @pytest.mark.asyncio
    async def test_get_sink_success(self, oam_service, mock_oam_client):
        """Test successful get_sink call."""
        # Setup mock response
        mock_oam_client.get_sink.return_value = {
            'Sink': {
                'Id': 'sink-1234567890abcdef0',
                'Arn': 'arn:aws:oam:us-east-1:123456789012:sink/sink-1234567890abcdef0',
                'Name': 'TestSink',
                'Status': 'ACTIVE'
            }
        }
        
        # Call the service method
        result = await oam_service.get_sink('sink-1234567890abcdef0')
        
        # Verify the result
        assert result['Sink']['Id'] == 'sink-1234567890abcdef0'
        assert result['Sink']['Name'] == 'TestSink'
        
        # Verify the client was called correctly
        mock_oam_client.get_sink.assert_called_once_with(SinkIdentifier='sink-1234567890abcdef0')

    @pytest.mark.asyncio
    async def test_list_links_success(self, oam_service, mock_oam_client):
        """Test successful list_links call."""
        # Setup mock response
        mock_oam_client.list_links.return_value = {
            'Links': [
                {
                    'Id': 'link-1234567890abcdef0',
                    'Arn': 'arn:aws:oam:us-east-1:123456789012:link/link-1234567890abcdef0',
                    'Label': 'TestLink',
                    'SinkArn': 'arn:aws:oam:us-east-1:123456789012:sink/sink-1234567890abcdef0',
                    'Status': 'ACTIVE'
                }
            ],
            'NextToken': None
        }
        
        # Call the service method
        result = await oam_service.list_links(
            sink_identifier='sink-1234567890abcdef0',
            max_results=10
        )
        
        # Verify the result
        assert len(result['Links']) == 1
        assert result['Links'][0]['Id'] == 'link-1234567890abcdef0'
        assert result['Links'][0]['Label'] == 'TestLink'
        
        # Verify the client was called correctly
        mock_oam_client.list_links.assert_called_once_with(
            SinkIdentifier='sink-1234567890abcdef0',
            MaxResults=10
        )

    @pytest.mark.asyncio
    async def test_get_link_success(self, oam_service, mock_oam_client):
        """Test successful get_link call."""
        # Setup mock response
        mock_oam_client.get_link.return_value = {
            'Link': {
                'Id': 'link-1234567890abcdef0',
                'Arn': 'arn:aws:oam:us-east-1:123456789012:link/link-1234567890abcdef0',
                'Label': 'TestLink',
                'SinkArn': 'arn:aws:oam:us-east-1:123456789012:sink/sink-1234567890abcdef0',
                'Status': 'ACTIVE'
            }
        }
        
        # Call the service method
        result = await oam_service.get_link('link-1234567890abcdef0')
        
        # Verify the result
        assert result['Link']['Id'] == 'link-1234567890abcdef0'
        assert result['Link']['Label'] == 'TestLink'
        
        # Verify the client was called correctly
        mock_oam_client.get_link.assert_called_once_with(LinkIdentifier='link-1234567890abcdef0')

    @pytest.mark.asyncio
    async def test_list_attached_links_success(self, oam_service, mock_oam_client):
        """Test successful list_attached_links call."""
        # Setup mock response
        mock_oam_client.list_attached_links.return_value = {
            'Links': [
                {
                    'Id': 'link-1234567890abcdef0',
                    'Arn': 'arn:aws:oam:us-east-1:123456789012:link/link-1234567890abcdef0',
                    'Label': 'TestLink',
                    'ResourceTypes': ['METRICS', 'LOGS'],
                    'Status': 'ACTIVE'
                }
            ],
            'NextToken': None
        }
        
        # Call the service method
        result = await oam_service.list_attached_links(
            sink_identifier='sink-1234567890abcdef0',
            max_results=10
        )
        
        # Verify the result
        assert len(result['Links']) == 1
        assert result['Links'][0]['Id'] == 'link-1234567890abcdef0'
        assert result['Links'][0]['Label'] == 'TestLink'
        
        # Verify the client was called correctly
        mock_oam_client.list_attached_links.assert_called_once_with(
            SinkIdentifier='sink-1234567890abcdef0',
            MaxResults=10
        )