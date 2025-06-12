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

"""Unit tests for the CloudWatch Logs service."""

import datetime
import pytest
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError

from awslabs.cloudwatch_mcp_server.services.logs_service import LogsService


@pytest.fixture
def mock_logs_client():
    """Create a mock CloudWatch Logs client."""
    mock_client = MagicMock()
    return mock_client


@pytest.fixture
def logs_service(mock_logs_client):
    """Create a LogsService instance with a mock client."""
    return LogsService(mock_logs_client)


class TestLogsService:
    """Tests for the LogsService class."""

    async def test_describe_log_groups_success(self, logs_service, mock_logs_client):
        """Test successful describe_log_groups call."""
        # Setup mock response for describe_log_groups
        mock_paginator = MagicMock()
        mock_logs_client.get_paginator.return_value = mock_paginator
        
        mock_page1 = {
            'logGroups': [
                {
                    'logGroupName': 'test-log-group',
                    'creationTime': 1609459200000,  # 2021-01-01T00:00:00Z
                    'metricFilterCount': 0,
                    'storedBytes': 1024,
                    'logGroupClass': 'STANDARD',
                    'logGroupArn': 'arn:aws:logs:us-east-1:123456789012:log-group:test-log-group'
                }
            ]
        }
        mock_paginator.paginate.return_value = [mock_page1]
        
        # Setup mock response for describe_query_definitions
        mock_logs_client.describe_query_definitions.return_value = {
            'queryDefinitions': [
                {
                    'queryDefinitionId': 'query-1',
                    'name': 'Test Query',
                    'queryString': 'fields @timestamp, @message | limit 20',
                    'logGroupNames': ['test-log-group']
                }
            ],
            'nextToken': None
        }
        
        # Call the service method
        result = await logs_service.describe_log_groups(
            log_group_name_prefix='test'
        )
        
        # Verify the result
        assert len(result.log_group_metadata) == 1
        assert result.log_group_metadata[0].logGroupName == 'test-log-group'
        assert result.log_group_metadata[0].logGroupArn == 'arn:aws:logs:us-east-1:123456789012:log-group:test-log-group'
        assert len(result.saved_queries) == 1
        assert result.saved_queries[0].name == 'Test Query'
        
        # Verify the client was called correctly
        mock_logs_client.get_paginator.assert_called_once_with('describe_log_groups')
        mock_paginator.paginate.assert_called_once()
        mock_logs_client.describe_query_definitions.assert_called_once()

    async def test_execute_log_insights_query_success(self, logs_service, mock_logs_client):
        """Test successful execute_log_insights_query call."""
        # Setup mock responses
        mock_logs_client.start_query.return_value = {
            'queryId': 'test-query-id'
        }
        
        mock_logs_client.get_query_results.return_value = {
            'status': 'Complete',
            'statistics': {
                'recordsMatched': 10,
                'recordsScanned': 100
            },
            'results': [
                [
                    {'field': '@timestamp', 'value': '2023-01-01 00:00:00.000'},
                    {'field': '@message', 'value': 'Test message'}
                ]
            ]
        }
        
        # Call the service method
        result = await logs_service.execute_log_insights_query(
            log_group_identifiers=['arn:aws:logs:us-east-1:123456789012:log-group:test-log-group'],
            start_time='2023-01-01T00:00:00+00:00',
            end_time='2023-01-02T00:00:00+00:00',
            query_string='fields @timestamp, @message | limit 10'
        )
        
        # Verify the result
        assert result['queryId'] == 'test-query-id'
        assert result['status'] == 'Complete'
        assert len(result['results']) == 1
        assert result['results'][0]['@timestamp'] == '2023-01-01 00:00:00.000'
        assert result['results'][0]['@message'] == 'Test message'
        
        # Verify the client was called correctly
        mock_logs_client.start_query.assert_called_once()
        mock_logs_client.get_query_results.assert_called_once_with(queryId='test-query-id')

    async def test_cancel_query_success(self, logs_service, mock_logs_client):
        """Test successful cancel_query call."""
        # Setup mock response
        mock_logs_client.stop_query.return_value = {
            'success': True
        }
        
        # Call the service method
        result = await logs_service.cancel_query(
            query_id='test-query-id'
        )
        
        # Verify the result
        assert result.success is True
        
        # Verify the client was called correctly
        mock_logs_client.stop_query.assert_called_once_with(queryId='test-query-id')