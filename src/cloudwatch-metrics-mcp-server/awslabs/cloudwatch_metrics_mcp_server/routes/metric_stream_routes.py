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

"""CloudWatch Metric Stream API routes."""

from typing import Dict, List, Optional
from mcp.server.fastmcp import Context
from pydantic import Field

from awslabs.cloudwatch_metrics_mcp_server.services.metric_stream_service import MetricStreamService
from awslabs.cloudwatch_metrics_mcp_server.services.client_factory import ClientFactory


# Initialize services
cloudwatch_client = ClientFactory.get_cloudwatch_client()
metric_stream_service = MetricStreamService(cloudwatch_client)


async def delete_metric_stream_route(
    ctx: Context,
    mcp,
    name: str = Field(
        ...,
        description='The name of the metric stream to delete.',
    ),
):
    """Route for delete_metric_stream API."""
    return await metric_stream_service.delete_metric_stream(
        name=name,
    )


async def get_metric_stream_route(
    ctx: Context,
    mcp,
    name: str = Field(
        ...,
        description='The name of the metric stream to retrieve.',
    ),
):
    """Route for get_metric_stream API."""
    return await metric_stream_service.get_metric_stream(
        name=name,
    )


async def list_metric_streams_route(
    ctx: Context,
    mcp,
    next_token: Optional[str] = Field(
        None,
        description='The token for the next set of results.',
    ),
    max_results: Optional[int] = Field(
        None,
        description='The maximum number of results to return.',
    ),
):
    """Route for list_metric_streams API."""
    return await metric_stream_service.list_metric_streams(
        next_token=next_token,
        max_results=max_results,
    )


async def put_metric_stream_route(
    ctx: Context,
    mcp,
    name: str = Field(
        ...,
        description='The name of the metric stream.',
    ),
    firehose_arn: str = Field(
        ...,
        description='The ARN of the Firehose delivery stream to use for this metric stream.',
    ),
    role_arn: str = Field(
        ...,
        description='The ARN of the IAM role that will be used to write to the Firehose delivery stream.',
    ),
    output_format: str = Field(
        ...,
        description='The output format of the metric stream. Valid values are json, opentelemetry0.7, and opentelemetry1.0.',
    ),
    include_filters: Optional[List[Dict]] = Field(
        None,
        description='If you specify this parameter, the stream sends metrics from only the metric namespaces that you specify here.',
    ),
    exclude_filters: Optional[List[Dict]] = Field(
        None,
        description='If you specify this parameter, the stream sends metrics from all metric namespaces except for the namespaces that you specify here.',
    ),
    statistics_configurations: Optional[List[Dict]] = Field(
        None,
        description='The list of statistics configurations for the metric stream.',
    ),
    include_linked_accounts_metrics: Optional[bool] = Field(
        None,
        description='If you are creating a metric stream in a monitoring account, specify true to include metrics from source accounts that are linked to this monitoring account.',
    ),
):
    """Route for put_metric_stream API."""
    return await metric_stream_service.put_metric_stream(
        name=name,
        firehose_arn=firehose_arn,
        role_arn=role_arn,
        output_format=output_format,
        include_filters=include_filters,
        exclude_filters=exclude_filters,
        statistics_configurations=statistics_configurations,
        include_linked_accounts_metrics=include_linked_accounts_metrics,
    )


async def start_metric_streams_route(
    ctx: Context,
    mcp,
    names: List[str] = Field(
        ...,
        description='The names of the metric streams to start.',
    ),
):
    """Route for start_metric_streams API."""
    return await metric_stream_service.start_metric_streams(
        names=names,
    )


async def stop_metric_streams_route(
    ctx: Context,
    mcp,
    names: List[str] = Field(
        ...,
        description='The names of the metric streams to stop.',
    ),
):
    """Route for stop_metric_streams API."""
    return await metric_stream_service.stop_metric_streams(
        names=names,
    )


def register_routes(mcp_server):
    """Register all metric stream routes with the MCP server."""
    mcp_server.tool(name='delete_metric_stream')(delete_metric_stream_route)
    mcp_server.tool(name='get_metric_stream')(get_metric_stream_route)
    mcp_server.tool(name='list_metric_streams')(list_metric_streams_route)
    mcp_server.tool(name='put_metric_stream')(put_metric_stream_route)
    mcp_server.tool(name='start_metric_streams')(start_metric_streams_route)
    mcp_server.tool(name='stop_metric_streams')(stop_metric_streams_route)