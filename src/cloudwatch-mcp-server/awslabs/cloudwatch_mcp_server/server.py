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

"""awslabs cloudwatch MCP Server implementation."""

import os
import sys
from awslabs.cloudwatch_mcp_server import MCP_SERVER_VERSION
from loguru import logger
from mcp.server.fastmcp import FastMCP

# Import tools
from awslabs.cloudwatch_mcp_server.tools.logs import CloudWatchLogsTool
from awslabs.cloudwatch_mcp_server.tools.alarms import AlarmsTool
from awslabs.cloudwatch_mcp_server.tools.oam.oam_tool import OAMTool
from awslabs.cloudwatch_mcp_server.tools.metric_streams.metric_streams_tool import MetricStreamsTool
from awslabs.cloudwatch_mcp_server.tools.dashboards.dashboards_tool import DashboardsTool
from awslabs.cloudwatch_mcp_server.tools.insight_rules import InsightRulesTool
from awslabs.cloudwatch_mcp_server.tools.anomaly_detectors import AnomalyDetectorsTool
from awslabs.cloudwatch_mcp_server.tools.tags import TagsTool
from awslabs.cloudwatch_mcp_server.tools.metrics import MetricsTool


mcp = FastMCP(
    'awslabs.cloudwatch-mcp-server',
    instructions='Use this MCP server to interact with CloudWatch. Supports retrieving metric data, managing dashboards, working with CloudWatch alarms, and analyzing CloudWatch Logs. With CloudWatch, you can monitor your AWS resources and applications in real-time, set alarms, create dashboards, visualize metrics, and analyze logs to help you respond to operational issues.',
    dependencies=[
        'pydantic',
        'loguru',
    ],
)

# Get AWS region from environment
aws_region: str = os.environ.get('AWS_REGION', 'us-east-1')

# Register all tools
def register_tools():
    """Register all tools with the MCP server."""
    logs_tool = CloudWatchLogsTool(region_name=aws_region)
    logs_tool.register(mcp)
    
    alarms_tool = AlarmsTool(region_name=aws_region)
    alarms_tool.register(mcp)
    
    oam_tool = OAMTool(region_name=aws_region)
    oam_tool.register(mcp)
    
    metric_streams_tool = MetricStreamsTool(region_name=aws_region)
    metric_streams_tool.register(mcp)
    
    dashboards_tool = DashboardsTool(region_name=aws_region)
    dashboards_tool.register(mcp)
    
    insight_rules_tool = InsightRulesTool(region_name=aws_region)
    insight_rules_tool.register(mcp)
    
    anomaly_detectors_tool = AnomalyDetectorsTool(region_name=aws_region)
    anomaly_detectors_tool.register(mcp)
    
    tags_tool = TagsTool(region_name=aws_region)
    tags_tool.register(mcp)
    
    metrics_tool = MetricsTool(region_name=aws_region)
    metrics_tool.register(mcp)


def main():
    """Run the MCP server."""
    # Register all tools
    register_tools()
    
    # Run the server
    mcp.run()
    
    logger.info('CloudWatch MCP server started')


if __name__ == '__main__':
    sys.exit(main())