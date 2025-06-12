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

"""Unit tests for the CloudWatch routes registration."""

import pytest
from unittest.mock import MagicMock

from awslabs.cloudwatch_mcp_server.routes import (
    alarm_routes,
    dashboard_routes,
    anomaly_detector_routes,
    metric_stream_routes,
    insight_rule_routes,
    tag_routes,
    metric_routes,
)


class TestRoutes:
    """Tests for the route registration functions."""

    def test_alarm_routes_registration(self):
        """Test that alarm_routes.register_routes can be called."""
        mock_mcp = MagicMock()
        alarm_routes.register_routes(mock_mcp)
        # Verify that tool was called for each route
        assert mock_mcp.tool.call_count == 9
        
    def test_dashboard_routes_registration(self):
        """Test that dashboard_routes.register_routes can be called."""
        mock_mcp = MagicMock()
        dashboard_routes.register_routes(mock_mcp)
        # Verify that tool was called for each route
        assert mock_mcp.tool.call_count == 4
        
    def test_anomaly_detector_routes_registration(self):
        """Test that anomaly_detector_routes.register_routes can be called."""
        mock_mcp = MagicMock()
        anomaly_detector_routes.register_routes(mock_mcp)
        # Verify that tool was called for each route
        assert mock_mcp.tool.call_count == 3
        
    def test_metric_stream_routes_registration(self):
        """Test that metric_stream_routes.register_routes can be called."""
        mock_mcp = MagicMock()
        metric_stream_routes.register_routes(mock_mcp)
        # Verify that tool was called for each route
        assert mock_mcp.tool.call_count == 6
        
    def test_insight_rule_routes_registration(self):
        """Test that insight_rule_routes.register_routes can be called."""
        mock_mcp = MagicMock()
        insight_rule_routes.register_routes(mock_mcp)
        # Verify that tool was called for each route
        assert mock_mcp.tool.call_count == 8
        
    def test_tag_routes_registration(self):
        """Test that tag_routes.register_routes can be called."""
        mock_mcp = MagicMock()
        tag_routes.register_routes(mock_mcp)
        # Verify that tool was called for each route
        assert mock_mcp.tool.call_count == 3
        
    def test_metric_routes_registration(self):
        """Test that metric_routes.register_routes can be called."""
        mock_mcp = MagicMock()
        metric_routes.register_routes(mock_mcp)
        # Verify that tool was called for each route
        assert mock_mcp.tool.call_count == 5