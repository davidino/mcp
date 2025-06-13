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

"""Tests for CloudWatch Metrics tool."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from awslabs.cloudwatch_mcp_server.tools.metrics.metrics_tool import (
    MetricsTool,
    MetricsOperation,
)
from awslabs.cloudwatch_mcp_server.models import (
    MetricList,
    MetricData,
    MetricDataResult,
    Metric,
    Dimension,
    MetricStatistics,
)


@pytest.fixture
def mock_context():
    """Create a mock MCP context."""
    ctx = MagicMock()
    ctx.error = AsyncMock()
    return ctx


@pytest.fixture
def mock_metric_service():
    """Create a mock MetricService."""
    service = MagicMock()
    service.list_metrics = AsyncMock()
    service.get_metric_data = AsyncMock()
    service.get_metric_statistics = AsyncMock()
    service.put_metric_data = AsyncMock()
    service.get_metric_widget_image = AsyncMock()
    return service


@pytest.fixture
def metrics_tool(mock_metric_service):
    """Create a MetricsTool with mocked service."""
    with patch('awslabs.cloudwatch_mcp_server.tools.metrics.metrics_tool.ClientFactory') as mock_factory:
        mock_factory.get_cloudwatch_client.return_value = MagicMock()
        tool = MetricsTool()
        tool.metric_service = mock_metric_service
        return tool


class TestMetricsTool:
    """Tests for the MetricsTool class."""

    async def test_list_metrics(self, metrics_tool, mock_context, mock_metric_service):
        """Test list_metrics operation."""
        mock_metric_service.list_metrics.return_value = MetricList(
            metrics=[
                Metric(
                    namespace="AWS/EC2",
                    metricName="CPUUtilization",
                    dimensions=[
                        Dimension(name="InstanceId", value="i-1234567890abcdef0")
                    ]
                )
            ]
        )
        
        result = await metrics_tool.cloudwatch_metrics(
            mock_context,
            operation=MetricsOperation.LIST_METRICS,
            namespace="AWS/EC2",
        )
        
        mock_metric_service.list_metrics.assert_called_once_with(
            namespace="AWS/EC2",
            metric_name=None,
            dimensions=None,
            max_items=None,
        )
        assert len(result.metrics) == 1
        assert result.metrics[0].namespace == "AWS/EC2"
        assert result.metrics[0].metricName == "CPUUtilization"

    async def test_get_metric_data(self, metrics_tool, mock_context, mock_metric_service):
        """Test get_metric_data operation."""
        mock_metric_service.get_metric_data.return_value = MetricData(
            metricDataResults=[
                MetricDataResult(
                    id="m1",
                    statusCode="Complete",
                    timestamps=["2025-01-01T00:00:00Z"],
                    values=[1.0],
                )
            ]
        )
        
        metric_data_queries = [
            {
                "Id": "m1",
                "MetricStat": {
                    "Metric": {
                        "Namespace": "AWS/EC2",
                        "MetricName": "CPUUtilization",
                    },
                    "Period": 300,
                    "Stat": "Average",
                }
            }
        ]
        
        result = await metrics_tool.cloudwatch_metrics(
            mock_context,
            operation=MetricsOperation.GET_METRIC_DATA,
            metric_data_queries=metric_data_queries,
            start_time="2025-01-01T00:00:00Z",
            end_time="2025-01-01T01:00:00Z",
        )
        
        mock_metric_service.get_metric_data.assert_called_once_with(
            metric_data_queries=metric_data_queries,
            start_time="2025-01-01T00:00:00Z",
            end_time="2025-01-01T01:00:00Z",
            scan_by=None,
            max_datapoints=None,
        )
        assert len(result.metricDataResults) == 1
        assert result.metricDataResults[0].id == "m1"
        assert result.metricDataResults[0].values == [1.0]

    async def test_get_metric_statistics(self, metrics_tool, mock_context, mock_metric_service):
        """Test get_metric_statistics operation."""
        mock_metric_service.get_metric_statistics.return_value = [
            MetricStatistics(
                timestamp="2025-01-01T00:00:00Z",
                average=1.0,
                sum=60.0,
                minimum=0.5,
                maximum=1.5,
                sampleCount=60,
            )
        ]
        
        result = await metrics_tool.cloudwatch_metrics(
            mock_context,
            operation=MetricsOperation.GET_METRIC_STATISTICS,
            namespace="AWS/EC2",
            metric_name="CPUUtilization",
            start_time="2025-01-01T00:00:00Z",
            end_time="2025-01-01T01:00:00Z",
            period=60,
            statistics=["Average", "Sum", "Minimum", "Maximum", "SampleCount"],
        )
        
        mock_metric_service.get_metric_statistics.assert_called_once_with(
            namespace="AWS/EC2",
            metric_name="CPUUtilization",
            dimensions=None,
            start_time="2025-01-01T00:00:00Z",
            end_time="2025-01-01T01:00:00Z",
            period=60,
            statistics=["Average", "Sum", "Minimum", "Maximum", "SampleCount"],
            unit=None,
        )
        assert len(result) == 1
        assert result[0].average == 1.0
        assert result[0].sum == 60.0

    async def test_put_metric_data(self, metrics_tool, mock_context, mock_metric_service):
        """Test put_metric_data operation."""
        mock_metric_service.put_metric_data.return_value = {
            "status": "Successfully published 1 metric data points to AWS/Custom"
        }
        
        metric_data = [
            {
                "MetricName": "RequestCount",
                "Value": 1.0,
            }
        ]
        
        result = await metrics_tool.cloudwatch_metrics(
            mock_context,
            operation=MetricsOperation.PUT_METRIC_DATA,
            namespace="AWS/Custom",
            metric_data=metric_data,
        )
        
        mock_metric_service.put_metric_data.assert_called_once_with(
            namespace="AWS/Custom",
            metric_data=metric_data,
        )
        assert "status" in result
        assert "Successfully published" in result["status"]

    async def test_get_metric_widget_image(self, metrics_tool, mock_context, mock_metric_service):
        """Test get_metric_widget_image operation."""
        mock_metric_service.get_metric_widget_image.return_value = {
            "metricWidgetImage": "base64_encoded_image"
        }
        
        metric_widget = {
            "width": 600,
            "height": 400,
            "metrics": [
                ["AWS/EC2", "CPUUtilization", "InstanceId", "i-1234567890abcdef0"]
            ],
            "period": 300,
            "stat": "Average",
            "title": "EC2 Instance CPU"
        }
        
        result = await metrics_tool.cloudwatch_metrics(
            mock_context,
            operation=MetricsOperation.GET_METRIC_WIDGET_IMAGE,
            metric_widget=metric_widget,
        )
        
        mock_metric_service.get_metric_widget_image.assert_called_once_with(
            metric_widget=metric_widget,
            output_format=None,
        )
        assert "metricWidgetImage" in result
        assert result["metricWidgetImage"] == "base64_encoded_image"

    async def test_missing_required_parameters(self, metrics_tool, mock_context):
        """Test error handling for missing required parameters."""
        with pytest.raises(ValueError) as excinfo:
            await metrics_tool.cloudwatch_metrics(
                mock_context,
                operation=MetricsOperation.GET_METRIC_DATA,
                start_time=None,
                end_time=None,
                metric_data_queries=None,
            )
        assert "metric_data_queries, start_time, and end_time are required" in str(excinfo.value)
        
        with pytest.raises(ValueError) as excinfo:
            await metrics_tool.cloudwatch_metrics(
                mock_context,
                operation=MetricsOperation.PUT_METRIC_DATA,
                namespace=None,
                metric_data=None,
            )
        assert "namespace and metric_data are required" in str(excinfo.value)

    async def test_unsupported_operation(self, metrics_tool, mock_context):
        """Test error handling for unsupported operations."""
        with pytest.raises(ValueError) as excinfo:
            await metrics_tool.cloudwatch_metrics(
                mock_context,
                operation="INVALID_OPERATION",
            )
        assert "Unsupported operation" in str(excinfo.value)