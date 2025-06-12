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
from awslabs.cloudwatch_mcp_server import MCP_SERVER_VERSION
from botocore.config import Config
from loguru import logger
from mcp.server.fastmcp import FastMCP

# Import services and routes
from awslabs.cloudwatch_mcp_server.services.client_factory import ClientFactory
from awslabs.cloudwatch_mcp_server.routes import (
    alarm_routes,
    dashboard_routes,
    anomaly_detector_routes,
    metric_stream_routes,
    insight_rule_routes,
    tag_routes,
    metric_routes,
    logs_routes,
)


mcp = FastMCP(
    'awslabs.cloudwatch-mcp-server',
    instructions='Use this MCP server to interact with CloudWatch. Supports retrieving metric data, managing dashboards, working with CloudWatch alarms, and analyzing CloudWatch Logs. With CloudWatch, you can monitor your AWS resources and applications in real-time, set alarms, create dashboards, visualize metrics, and analyze logs to help you respond to operational issues.',
    dependencies=[
        'pydantic',
        'loguru',
    ],
)

# Initialize client
aws_region: str = os.environ.get('AWS_REGION', 'us-east-1')
config = Config(user_agent_extra=f'awslabs/mcp/cloudwatch-mcp-server/{MCP_SERVER_VERSION}')

try:
    cloudwatch_client = ClientFactory.get_cloudwatch_client()
except Exception as e:
    logger.error(f'Error creating cloudwatch client: {str(e)}')
    raise


# Register all routes
def register_routes():
    """Register all routes with the MCP server."""
    alarm_routes.register_routes(mcp)
    dashboard_routes.register_routes(mcp)
    anomaly_detector_routes.register_routes(mcp)
    metric_stream_routes.register_routes(mcp)
    insight_rule_routes.register_routes(mcp)
    tag_routes.register_routes(mcp)
    metric_routes.register_routes(mcp)
    logs_routes.register_routes(mcp)


def main():
    """Run the MCP server."""
    # Register all routes
    register_routes()
    
    # Run the server
    mcp.run()
    
    logger.info('CloudWatch MCP server started')


if __name__ == '__main__':
    main()