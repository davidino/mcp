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

"""CloudWatch Anomaly Detector API routes."""

from typing import Dict, List, Optional
from mcp.server.fastmcp import Context
from pydantic import Field

from awslabs.cloudwatch_metrics_mcp_server.services.anomaly_detector_service import AnomalyDetectorService
from awslabs.cloudwatch_metrics_mcp_server.services.client_factory import ClientFactory


# Initialize services
cloudwatch_client = ClientFactory.get_cloudwatch_client()
anomaly_detector_service = AnomalyDetectorService(cloudwatch_client)


async def delete_anomaly_detector_route(
    ctx: Context,
    mcp,
    namespace: str = Field(
        ...,
        description='The namespace of the metric.',
    ),
    metric_name: str = Field(
        ...,
        description='The name of the metric.',
    ),
    dimensions: Optional[List[Dict[str, str]]] = Field(
        None,
        description='The dimensions of the metric. Each dimension is a dictionary with "Name" and "Value" keys.',
    ),
    stat: Optional[str] = Field(
        None,
        description='The statistic of the metric.',
    ),
    single_metric_anomaly_detector: Optional[Dict] = Field(
        None,
        description='A single metric anomaly detector to delete.',
    ),
    metric_math_anomaly_detector: Optional[Dict] = Field(
        None,
        description='A metric math anomaly detector to delete.',
    ),
):
    """Route for delete_anomaly_detector API."""
    return await anomaly_detector_service.delete_anomaly_detector(
        namespace=namespace,
        metric_name=metric_name,
        dimensions=dimensions,
        stat=stat,
        single_metric_anomaly_detector=single_metric_anomaly_detector,
        metric_math_anomaly_detector=metric_math_anomaly_detector,
    )


async def describe_anomaly_detectors_route(
    ctx: Context,
    mcp,
    namespace: Optional[str] = Field(
        None,
        description='The namespace of the metric.',
    ),
    metric_name: Optional[str] = Field(
        None,
        description='The name of the metric.',
    ),
    dimensions: Optional[List[Dict[str, str]]] = Field(
        None,
        description='The dimensions of the metric. Each dimension is a dictionary with "Name" and "Value" keys.',
    ),
    stat: Optional[str] = Field(
        None,
        description='The statistic of the metric.',
    ),
    next_token: Optional[str] = Field(
        None,
        description='The token for the next set of results.',
    ),
    max_results: Optional[int] = Field(
        None,
        description='The maximum number of results to return.',
    ),
):
    """Route for describe_anomaly_detectors API."""
    return await anomaly_detector_service.describe_anomaly_detectors(
        namespace=namespace,
        metric_name=metric_name,
        dimensions=dimensions,
        stat=stat,
        next_token=next_token,
        max_results=max_results,
    )


async def put_anomaly_detector_route(
    ctx: Context,
    mcp,
    namespace: str = Field(
        ...,
        description='The namespace of the metric.',
    ),
    metric_name: str = Field(
        ...,
        description='The name of the metric.',
    ),
    dimensions: Optional[List[Dict[str, str]]] = Field(
        None,
        description='The dimensions of the metric. Each dimension is a dictionary with "Name" and "Value" keys.',
    ),
    stat: Optional[str] = Field(
        None,
        description='The statistic of the metric.',
    ),
    configuration: Optional[Dict] = Field(
        None,
        description='The configuration for the anomaly detection model.',
    ),
    single_metric_anomaly_detector: Optional[Dict] = Field(
        None,
        description='A single metric anomaly detector to create or update.',
    ),
    metric_math_anomaly_detector: Optional[Dict] = Field(
        None,
        description='A metric math anomaly detector to create or update.',
    ),
):
    """Route for put_anomaly_detector API."""
    return await anomaly_detector_service.put_anomaly_detector(
        namespace=namespace,
        metric_name=metric_name,
        dimensions=dimensions,
        stat=stat,
        configuration=configuration,
        single_metric_anomaly_detector=single_metric_anomaly_detector,
        metric_math_anomaly_detector=metric_math_anomaly_detector,
    )


def register_routes(mcp_server):
    """Register all anomaly detector routes with the MCP server."""
    mcp_server.tool(name='delete_anomaly_detector')(delete_anomaly_detector_route)
    mcp_server.tool(name='desc_anomaly_detectors')(describe_anomaly_detectors_route)
    mcp_server.tool(name='put_anomaly_detector')(put_anomaly_detector_route)