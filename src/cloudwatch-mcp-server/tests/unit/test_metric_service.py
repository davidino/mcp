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

"""Unit tests for the CloudWatch Metric service."""

import datetime
import pytest
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError

from awslabs.cloudwatch_mcp_server.services.metric_service import MetricService


@pytest.fixture
def mock_cloudwatch_client():
    """Create a mock CloudWatch client."""
    mock_client = MagicMock()
    return mock_client


@pytest.fixture
def metric_service(mock_cloudwatch_client):
    """Create a MetricService instance with a mock client."""
    return MetricService(mock_cloudwatch_client)


class TestMetricService:
    """Tests for the MetricService class."""

    async def test_list_metrics_success(self, metric_service, mock_cloudwatch_client):
        """Test successful list_metrics call."""
        # Setup mock response
        mock_paginator = MagicMock()
        mock_cloudwatch_client.get_paginator.return_value = mock_paginator
        
        mock_page1 = {
            'Metrics': [
                {
                    'Namespace': 'AWS/EC2',
                    'MetricName': 'CPUUtilization',
                    'Dimensions': [
                        {'Name': 'InstanceId', 'Value': 'i-1234567890abcdef0'}
                    ]
                }
            ]
        }
        mock_paginator.paginate.return_value = [mock_page1]
        
        # Call the service method
        result = await metric_service.list_metrics(
            namespace='AWS/EC2',
            metric_name='CPUUtilization'
        )
        
        # Verify the result
        assert len(result.metrics) == 1
        assert result.metrics[0].namespace == 'AWS/EC2'
        assert result.metrics[0].metricName == 'CPUUtilization'
        assert len(result.metrics[0].dimensions) == 1
        assert result.metrics[0].dimensions[0].name == 'InstanceId'
        assert result.metrics[0].dimensions[0].value == 'i-1234567890abcdef0'
        
        # Verify the client was called correctly
        mock_cloudwatch_client.get_paginator.assert_called_once_with('list_metrics')
        mock_paginator.paginate.assert_called_once()

    async def test_list_metrics_client_error(self, metric_service, mock_cloudwatch_client):
        """Test list_metrics with ClientError."""
        # Setup mock to raise ClientError
        mock_cloudwatch_client.get_paginator.side_effect = ClientError(
            {'Error': {'Code': 'InvalidParameterValue', 'Message': 'Test error'}},
            'ListMetrics'
        )
        
        # Call the service method and expect exception
        with pytest.raises(ClientError):
            await metric_service.list_metrics()

    async def test_get_metric_data_success(self, metric_service, mock_cloudwatch_client):
        """Test successful get_metric_data call."""
        # Setup mock response
        mock_cloudwatch_client.get_metric_data.return_value = {
            'MetricDataResults': [
                {
                    'Id': 'cpu1',
                    'Label': 'CPUUtilization',
                    'StatusCode': 'Complete',
                    'Timestamps': [datetime.datetime(2023, 1, 1, 12, 0, 0)],
                    'Values': [45.5],
                }
            ],
            'NextToken': None,
            'Messages': []
        }
        
        # Call the service method
        result = await metric_service.get_metric_data(
            metric_data_queries=[{'Id': 'cpu1', 'MetricStat': {'Metric': {'Namespace': 'AWS/EC2'}}}],
            start_time='2023-01-01T00:00:00+00:00',
            end_time='2023-01-02T00:00:00+00:00'
        )
        
        # Verify the result
        assert len(result.metricDataResults) == 1
        assert result.metricDataResults[0].id == 'cpu1'
        assert result.metricDataResults[0].label == 'CPUUtilization'
        assert result.metricDataResults[0].statusCode == 'Complete'
        assert len(result.metricDataResults[0].timestamps) == 1
        assert len(result.metricDataResults[0].values) == 1
        assert result.metricDataResults[0].values[0] == 45.5
        
        # Verify the client was called correctly
        mock_cloudwatch_client.get_metric_data.assert_called_once()

    async def test_get_metric_statistics_success(self, metric_service, mock_cloudwatch_client):
        """Test successful get_metric_statistics call."""
        # Setup mock response
        mock_cloudwatch_client.get_metric_statistics.return_value = {
            'Datapoints': [
                {
                    'Timestamp': datetime.datetime(2023, 1, 1, 12, 0, 0),
                    'Average': 45.5,
                    'SampleCount': 5.0,
                    'Sum': 227.5,
                    'Minimum': 40.0,
                    'Maximum': 50.0,
                }
            ]
        }
        
        # Call the service method
        result = await metric_service.get_metric_statistics(
            namespace='AWS/EC2',
            metric_name='CPUUtilization',
            start_time='2023-01-01T00:00:00+00:00',
            end_time='2023-01-02T00:00:00+00:00',
            period=3600,
            statistics=['Average', 'SampleCount', 'Sum', 'Minimum', 'Maximum']
        )
        
        # Verify the result
        assert len(result) == 1
        assert result[0].average == 45.5
        assert result[0].sampleCount == 5.0
        assert result[0].sum == 227.5
        assert result[0].minimum == 40.0
        assert result[0].maximum == 50.0
        
        # Verify the client was called correctly
        mock_cloudwatch_client.get_metric_statistics.assert_called_once()

    async def test_put_metric_data_success(self, metric_service, mock_cloudwatch_client):
        """Test successful put_metric_data call."""
        # Setup mock response
        mock_cloudwatch_client.put_metric_data.return_value = {}
        
        # Call the service method
        result = await metric_service.put_metric_data(
            namespace='CustomNamespace',
            metric_data=[
                {
                    'MetricName': 'CustomMetric',
                    'Value': 42.0
                }
            ]
        )
        
        # Verify the result
        assert result['status'] == 'Successfully published 1 metric data points to CustomNamespace'
        
        # Verify the client was called correctly
        mock_cloudwatch_client.put_metric_data.assert_called_once_with(
            Namespace='CustomNamespace',
            MetricData=[{'MetricName': 'CustomMetric', 'Value': 42.0}]
        )

    async def test_get_metric_widget_image_success(self, metric_service, mock_cloudwatch_client):
        """Test successful get_metric_widget_image call with string input."""
        # Setup mock response with binary data
        mock_cloudwatch_client.get_metric_widget_image.return_value = {
            'MetricWidgetImage': b'fake-image-data'
        }
        
        # Call the service method
        result = await metric_service.get_metric_widget_image(
            metric_widget='{"metrics": [["AWS/EC2", "CPUUtilization"]]}'
        )
        
        # Verify the result contains base64-encoded image
        assert 'metricWidgetImage' in result
        
        # Verify the client was called correctly
        mock_cloudwatch_client.get_metric_widget_image.assert_called_once_with(
            MetricWidget='{"metrics": [["AWS/EC2", "CPUUtilization"]]}'
        )
        
    async def test_get_metric_widget_image_with_dict(self, metric_service, mock_cloudwatch_client):
        """Test get_metric_widget_image with dictionary input."""
        # Setup mock response with binary data
        mock_cloudwatch_client.get_metric_widget_image.return_value = {
            'MetricWidgetImage': b'fake-image-data'
        }
        
        # Call the service method with a dictionary
        result = await metric_service.get_metric_widget_image(
            metric_widget={"metrics": [["AWS/EC2", "CPUUtilization"]]}
        )
        
        # Verify the result contains base64-encoded image
        assert 'metricWidgetImage' in result
        
        # Verify the client was called correctly with JSON string
        mock_cloudwatch_client.get_metric_widget_image.assert_called_once_with(
            MetricWidget='{"metrics": [["AWS/EC2", "CPUUtilization"]]}'
        )
        
    async def test_get_metric_widget_image_invalid_json(self, metric_service):
        """Test get_metric_widget_image with invalid JSON string."""
        # Call the service method with invalid JSON
        with pytest.raises(ValueError) as excinfo:
            await metric_service.get_metric_widget_image(
                metric_widget='{invalid json}'
            )
        
        # Verify the error message
        assert "must be a valid JSON string" in str(excinfo.value)