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

"""Unit tests for the CloudWatch Dashboard service."""

import pytest
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError

from awslabs.cloudwatch_mcp_server.services.dashboard_service import DashboardService


@pytest.fixture
def mock_cloudwatch_client():
    """Create a mock CloudWatch client."""
    mock_client = MagicMock()
    return mock_client


@pytest.fixture
def dashboard_service(mock_cloudwatch_client):
    """Create a DashboardService instance with a mock client."""
    return DashboardService(mock_cloudwatch_client)


class TestDashboardService:
    """Tests for the DashboardService class."""

    async def test_get_dashboard_success(self, dashboard_service, mock_cloudwatch_client):
        """Test successful get_dashboard call."""
        # Setup mock response
        mock_cloudwatch_client.get_dashboard.return_value = {
            'DashboardName': 'TestDashboard',
            'DashboardArn': 'arn:aws:cloudwatch:us-east-1:123456789012:dashboard/TestDashboard',
            'DashboardBody': '{"widgets":[]}',
            'Size': 100
        }
        
        # Call the service method
        result = await dashboard_service.get_dashboard(
            dashboard_name='TestDashboard'
        )
        
        # Verify the result
        assert result['dashboardName'] == 'TestDashboard'
        assert result['dashboardArn'] == 'arn:aws:cloudwatch:us-east-1:123456789012:dashboard/TestDashboard'
        assert result['dashboardBody'] == '{"widgets":[]}'
        assert result['size'] == 100
        
        # Verify the client was called correctly
        mock_cloudwatch_client.get_dashboard.assert_called_once_with(
            DashboardName='TestDashboard'
        )

    async def test_list_dashboards_success(self, dashboard_service, mock_cloudwatch_client):
        """Test successful list_dashboards call."""
        # Setup mock response
        mock_cloudwatch_client.list_dashboards.return_value = {
            'DashboardEntries': [
                {
                    'DashboardName': 'TestDashboard1',
                    'DashboardArn': 'arn:aws:cloudwatch:us-east-1:123456789012:dashboard/TestDashboard1',
                    'LastModified': '2023-01-01T00:00:00Z',
                    'Size': 100
                },
                {
                    'DashboardName': 'TestDashboard2',
                    'DashboardArn': 'arn:aws:cloudwatch:us-east-1:123456789012:dashboard/TestDashboard2',
                    'LastModified': '2023-01-02T00:00:00Z',
                    'Size': 200
                }
            ],
            'NextToken': None
        }
        
        # Call the service method
        result = await dashboard_service.list_dashboards(
            dashboard_name_prefix='Test'
        )
        
        # Verify the result
        assert len(result['dashboardEntries']) == 2
        assert result['dashboardEntries'][0]['DashboardName'] == 'TestDashboard1'
        assert result['dashboardEntries'][1]['DashboardName'] == 'TestDashboard2'
        
        # Verify the client was called correctly
        mock_cloudwatch_client.list_dashboards.assert_called_once_with(
            DashboardNamePrefix='Test'
        )

    async def test_put_dashboard_success(self, dashboard_service, mock_cloudwatch_client):
        """Test successful put_dashboard call."""
        # Setup mock response
        mock_cloudwatch_client.put_dashboard.return_value = {
            'DashboardValidationMessages': []
        }
        
        # Call the service method
        result = await dashboard_service.put_dashboard(
            dashboard_name='TestDashboard',
            dashboard_body='{"widgets":[]}'
        )
        
        # Verify the result
        assert 'dashboardValidationMessages' in result
        assert len(result['dashboardValidationMessages']) == 0
        
        # Verify the client was called correctly
        mock_cloudwatch_client.put_dashboard.assert_called_once_with(
            DashboardName='TestDashboard',
            DashboardBody='{"widgets":[]}'
        )
        
    async def test_put_dashboard_with_dict(self, dashboard_service, mock_cloudwatch_client):
        """Test put_dashboard with dictionary input."""
        # Setup mock response
        mock_cloudwatch_client.put_dashboard.return_value = {
            'DashboardValidationMessages': []
        }
        
        # Call the service method with a dictionary
        result = await dashboard_service.put_dashboard(
            dashboard_name='TestDashboard',
            dashboard_body={"widgets": []}
        )
        
        # Verify the result
        assert 'dashboardValidationMessages' in result
        
        # Verify the client was called correctly with JSON string
        mock_cloudwatch_client.put_dashboard.assert_called_once_with(
            DashboardName='TestDashboard',
            DashboardBody='{"widgets": []}'
        )
        
    async def test_put_dashboard_invalid_json(self, dashboard_service):
        """Test put_dashboard with invalid JSON string."""
        # Call the service method with invalid JSON
        with pytest.raises(ValueError) as excinfo:
            await dashboard_service.put_dashboard(
                dashboard_name='TestDashboard',
                dashboard_body='{invalid json}'
            )
        
        # Verify the error message
        assert "must be a valid JSON string" in str(excinfo.value)

    async def test_delete_dashboards_success(self, dashboard_service, mock_cloudwatch_client):
        """Test successful delete_dashboards call."""
        # Setup mock response
        mock_cloudwatch_client.delete_dashboards.return_value = {}
        
        # Call the service method
        result = await dashboard_service.delete_dashboards(
            dashboard_names=['TestDashboard1', 'TestDashboard2']
        )
        
        # Verify the result
        assert result['status'] == 'Successfully deleted 2 dashboards'
        
        # Verify the client was called correctly
        mock_cloudwatch_client.delete_dashboards.assert_called_once_with(
            DashboardNames=['TestDashboard1', 'TestDashboard2']
        )