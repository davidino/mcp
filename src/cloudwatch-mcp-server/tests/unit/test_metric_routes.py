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

"""Unit tests for the CloudWatch Metric routes."""

import pytest
from unittest.mock import MagicMock, patch

from awslabs.cloudwatch_metrics_mcp_server.routes import metric_routes


class TestMetricRoutes:
    """Tests for the metric routes."""

    def test_register_routes(self):
        """Test that register_routes registers all routes."""
        mock_mcp = MagicMock()
        metric_routes.register_routes(mock_mcp)
        
        # Verify that tool was called for each route
        assert mock_mcp.tool.call_count == 5
        
        # Verify that each route was registered with the correct name
        route_names = []
        for call in mock_mcp.tool.call_args_list:
            # Extract the name parameter from the call
            name = call[1]['name']
            route_names.append(name)
            
        assert 'list_metrics' in route_names
        assert 'get_metric_data' in route_names
        assert 'get_metric_statistics' in route_names
        assert 'put_metric_data' in route_names
        assert 'get_metric_widget_image' in route_names