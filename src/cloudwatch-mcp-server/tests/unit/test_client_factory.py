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

"""Unit tests for the AWS client factory."""

import os
import pytest
from unittest.mock import patch, MagicMock

from awslabs.cloudwatch_mcp_server.services.client_factory import ClientFactory


class TestClientFactory:
    """Tests for the ClientFactory class."""

    @patch('boto3.Session')
    def test_get_cloudwatch_client_with_region(self, mock_session):
        """Test get_cloudwatch_client with region parameter."""
        # Setup mock
        mock_boto3_session = MagicMock()
        mock_session.return_value = mock_boto3_session
        mock_client = MagicMock()
        mock_boto3_session.client.return_value = mock_client
        
        # Call the factory method
        client = ClientFactory.get_cloudwatch_client(region_name='us-west-2')
        
        # Verify the session was created with the correct region
        mock_session.assert_called_once()
        assert mock_session.call_args[1]['region_name'] == 'us-west-2'
        
        # Verify the client was created
        mock_boto3_session.client.assert_called_once()
        assert mock_boto3_session.client.call_args[0][0] == 'cloudwatch'

    @patch('boto3.Session')
    def test_get_cloudwatch_client_with_profile(self, mock_session):
        """Test get_cloudwatch_client with profile parameter."""
        # Setup mock
        mock_boto3_session = MagicMock()
        mock_session.return_value = mock_boto3_session
        mock_client = MagicMock()
        mock_boto3_session.client.return_value = mock_client
        
        # Call the factory method
        client = ClientFactory.get_cloudwatch_client(profile_name='test-profile')
        
        # Verify the session was created with the correct profile
        mock_session.assert_called_once()
        assert mock_session.call_args[1]['profile_name'] == 'test-profile'
        
        # Verify the client was created
        mock_boto3_session.client.assert_called_once()
        assert mock_boto3_session.client.call_args[0][0] == 'cloudwatch'

    @patch('boto3.Session')
    @patch.dict(os.environ, {'AWS_REGION': 'us-east-2'})
    def test_get_cloudwatch_client_with_env_region(self, mock_session):
        """Test get_cloudwatch_client with region from environment."""
        # Setup mock
        mock_boto3_session = MagicMock()
        mock_session.return_value = mock_boto3_session
        mock_client = MagicMock()
        mock_boto3_session.client.return_value = mock_client
        
        # Call the factory method
        client = ClientFactory.get_cloudwatch_client()
        
        # Verify the session was created with the region from environment
        mock_session.assert_called_once()
        assert mock_session.call_args[1]['region_name'] == 'us-east-2'
        
        # Verify the client was created
        mock_boto3_session.client.assert_called_once()
        assert mock_boto3_session.client.call_args[0][0] == 'cloudwatch'

    @patch('boto3.Session')
    @patch.dict(os.environ, {'AWS_PROFILE': 'dev-profile'})
    def test_get_cloudwatch_client_with_env_profile(self, mock_session):
        """Test get_cloudwatch_client with profile from environment."""
        # Setup mock
        mock_boto3_session = MagicMock()
        mock_session.return_value = mock_boto3_session
        mock_client = MagicMock()
        mock_boto3_session.client.return_value = mock_client
        
        # Call the factory method
        client = ClientFactory.get_cloudwatch_client()
        
        # Verify the session was created with the profile from environment
        mock_session.assert_called_once()
        assert mock_session.call_args[1]['profile_name'] == 'dev-profile'
        
        # Verify the client was created
        mock_boto3_session.client.assert_called_once()
        assert mock_boto3_session.client.call_args[0][0] == 'cloudwatch'