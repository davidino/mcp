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

"""Tests for CloudWatch Anomaly Detectors tool."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from awslabs.cloudwatch_mcp_server.tools.anomaly_detectors.anomaly_detectors_tool import (
    AnomalyDetectorsTool,
    AnomalyDetectorsOperation,
)


@pytest.fixture
def mock_context():
    """Create a mock MCP context."""
    ctx = MagicMock()
    ctx.error = AsyncMock()
    return ctx


@pytest.fixture
def mock_anomaly_detector_service():
    """Create a mock AnomalyDetectorService."""
    service = MagicMock()
    service.delete_anomaly_detector = AsyncMock()
    service.describe_anomaly_detectors = AsyncMock()
    service.put_anomaly_detector = AsyncMock()
    return service


@pytest.fixture
def anomaly_detectors_tool(mock_anomaly_detector_service):
    """Create an AnomalyDetectorsTool with mocked service."""
    with patch('awslabs.cloudwatch_mcp_server.tools.anomaly_detectors.anomaly_detectors_tool.ClientFactory') as mock_factory:
        mock_factory.get_cloudwatch_client.return_value = MagicMock()
        tool = AnomalyDetectorsTool()
        tool.anomaly_detector_service = mock_anomaly_detector_service
        return tool


class TestAnomalyDetectorsTool:
    """Tests for the AnomalyDetectorsTool class."""

    async def test_delete_anomaly_detector(self, anomaly_detectors_tool, mock_context, mock_anomaly_detector_service):
        """Test delete_anomaly_detector operation."""
        mock_anomaly_detector_service.delete_anomaly_detector.return_value = {
            "status": "Successfully deleted anomaly detector for AWS/EC2:CPUUtilization"
        }
        
        result = await anomaly_detectors_tool.cloudwatch_anomaly_detectors(
            mock_context,
            operation=AnomalyDetectorsOperation.DELETE_ANOMALY_DETECTOR,
            namespace="AWS/EC2",
            metric_name="CPUUtilization",
        )
        
        mock_anomaly_detector_service.delete_anomaly_detector.assert_called_once_with(
            namespace="AWS/EC2",
            metric_name="CPUUtilization",
            dimensions=None,
            stat=None,
            single_metric_anomaly_detector=None,
            metric_math_anomaly_detector=None,
        )
        assert result["status"] == "Successfully deleted anomaly detector for AWS/EC2:CPUUtilization"

    async def test_describe_anomaly_detectors(self, anomaly_detectors_tool, mock_context, mock_anomaly_detector_service):
        """Test describe_anomaly_detectors operation."""
        mock_anomaly_detector_service.describe_anomaly_detectors.return_value = {
            "anomalyDetectors": [{"Namespace": "AWS/EC2", "MetricName": "CPUUtilization"}],
            "nextToken": None
        }
        
        result = await anomaly_detectors_tool.cloudwatch_anomaly_detectors(
            mock_context,
            operation=AnomalyDetectorsOperation.DESCRIBE_ANOMALY_DETECTORS,
        )
        
        mock_anomaly_detector_service.describe_anomaly_detectors.assert_called_once_with(
            namespace=None,
            metric_name=None,
            dimensions=None,
            stat=None,
            next_token=None,
            max_results=None,
        )
        assert len(result["anomalyDetectors"]) == 1
        assert result["anomalyDetectors"][0]["Namespace"] == "AWS/EC2"

    async def test_put_anomaly_detector(self, anomaly_detectors_tool, mock_context, mock_anomaly_detector_service):
        """Test put_anomaly_detector operation."""
        mock_anomaly_detector_service.put_anomaly_detector.return_value = {
            "status": "Successfully created or updated anomaly detector for AWS/EC2:CPUUtilization"
        }
        
        result = await anomaly_detectors_tool.cloudwatch_anomaly_detectors(
            mock_context,
            operation=AnomalyDetectorsOperation.PUT_ANOMALY_DETECTOR,
            namespace="AWS/EC2",
            metric_name="CPUUtilization",
        )
        
        mock_anomaly_detector_service.put_anomaly_detector.assert_called_once_with(
            namespace="AWS/EC2",
            metric_name="CPUUtilization",
            dimensions=None,
            stat=None,
            configuration=None,
            single_metric_anomaly_detector=None,
            metric_math_anomaly_detector=None,
        )
        assert result["status"] == "Successfully created or updated anomaly detector for AWS/EC2:CPUUtilization"

    async def test_missing_required_parameters(self, anomaly_detectors_tool, mock_context):
        """Test error handling for missing required parameters."""
        with pytest.raises(ValueError) as excinfo:
            await anomaly_detectors_tool.cloudwatch_anomaly_detectors(
                mock_context,
                operation=AnomalyDetectorsOperation.DELETE_ANOMALY_DETECTOR,
                namespace=None,
                metric_name=None,
            )
        assert "namespace and metric_name are required" in str(excinfo.value)

    async def test_unsupported_operation(self, anomaly_detectors_tool, mock_context):
        """Test error handling for unsupported operations."""
        with pytest.raises(ValueError) as excinfo:
            await anomaly_detectors_tool.cloudwatch_anomaly_detectors(
                mock_context,
                operation="INVALID_OPERATION",
            )
        assert "Unsupported operation" in str(excinfo.value)