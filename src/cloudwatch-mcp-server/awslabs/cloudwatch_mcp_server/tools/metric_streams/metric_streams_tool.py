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

"""CloudWatch Metric Streams tool implementation."""

from enum import Enum
from typing import Dict, List, Optional, Any
from loguru import logger
from mcp.server.fastmcp import Context

from awslabs.cloudwatch_mcp_server.services.metric_stream_service import MetricStreamService
from awslabs.cloudwatch_mcp_server.services.client_factory import ClientFactory


class MetricStreamsOperation(str, Enum):
    """Enum for CloudWatch Metric Streams operations."""
    DELETE_METRIC_STREAM = "delete_metric_stream"
    GET_METRIC_STREAM = "get_metric_stream"
    LIST_METRIC_STREAMS = "list_metric_streams"
    PUT_METRIC_STREAM = "put_metric_stream"
    START_METRIC_STREAMS = "start_metric_streams"
    STOP_METRIC_STREAMS = "stop_metric_streams"


class MetricStreamsTool:
    """Tool for working with CloudWatch Metric Streams."""
    
    def __init__(self, region_name: str = "us-east-1"):
        """Initialize the CloudWatch Metric Streams tool.
        
        Args:
            region_name: AWS region name.
        """
        self.region_name = region_name
        cloudwatch_client = ClientFactory.get_cloudwatch_client(region_name=region_name)
        self.metric_stream_service = MetricStreamService(cloudwatch_client)
    
    async def cloudwatch_metric_streams(
        self,
        ctx: Context,
        operation: MetricStreamsOperation,
        # Parameters for stream operations
        name: Optional[str] = None,
        names: Optional[List[str]] = None,
        # Parameters for put_metric_stream
        firehose_arn: Optional[str] = None,
        role_arn: Optional[str] = None,
        output_format: Optional[str] = None,
        include_filters: Optional[List[Dict]] = None,
        exclude_filters: Optional[List[Dict]] = None,
        statistics_configurations: Optional[List[Dict]] = None,
        include_linked_accounts_metrics: Optional[bool] = None,
        # Pagination parameters
        next_token: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Perform CloudWatch Metric Streams operations.
        
        Args:
            ctx: The MCP context.
            operation: The operation to perform.
            
            # Parameters for stream operations
            name: The name of the metric stream.
            names: The names of the metric streams (for start/stop operations).
            
            # Parameters for put_metric_stream
            firehose_arn: The ARN of the Firehose delivery stream.
            role_arn: The ARN of the IAM role.
            output_format: The output format of the metric stream.
            include_filters: Filters to include specific metric namespaces.
            exclude_filters: Filters to exclude specific metric namespaces.
            statistics_configurations: Statistics configurations for the metric stream.
            include_linked_accounts_metrics: Whether to include metrics from linked accounts.
            
            # Pagination parameters
            next_token: Token for pagination.
            max_results: Maximum number of results to return.
            
        Returns:
            The result of the operation, which varies based on the operation type.
        """
        try:
            if operation == MetricStreamsOperation.DELETE_METRIC_STREAM:
                if not name:
                    raise ValueError("name is required for delete_metric_stream operation")
                
                return await self._delete_metric_stream(
                    ctx,
                    name=name,
                )
            if operation == MetricStreamsOperation.GET_METRIC_STREAM:
                if not name:
                    raise ValueError("name is required for get_metric_stream operation")
                
                return await self._get_metric_stream(
                    ctx,
                    name=name,
                )
            if operation == MetricStreamsOperation.LIST_METRIC_STREAMS:
                return await self._list_metric_streams(
                    ctx,
                    next_token=next_token,
                    max_results=max_results,
                )
            if operation == MetricStreamsOperation.PUT_METRIC_STREAM:
                if not name or not firehose_arn or not role_arn or not output_format:
                    raise ValueError("name, firehose_arn, role_arn, and output_format are required for put_metric_stream operation")
                
                return await self._put_metric_stream(
                    ctx,
                    name=name,
                    firehose_arn=firehose_arn,
                    role_arn=role_arn,
                    output_format=output_format,
                    include_filters=include_filters,
                    exclude_filters=exclude_filters,
                    statistics_configurations=statistics_configurations,
                    include_linked_accounts_metrics=include_linked_accounts_metrics,
                )
            if operation == MetricStreamsOperation.START_METRIC_STREAMS:
                if not names:
                    raise ValueError("names is required for start_metric_streams operation")
                
                return await self._start_metric_streams(
                    ctx,
                    names=names,
                )
            if operation == MetricStreamsOperation.STOP_METRIC_STREAMS:
                if not names:
                    raise ValueError("names is required for stop_metric_streams operation")
                
                return await self._stop_metric_streams(
                    ctx,
                    names=names,
                )
            else:
                raise ValueError(f"Unsupported operation: {operation}")
        except Exception as e:
            logger.error(f"Error in cloudwatch_metric_streams tool: {str(e)}")
            await ctx.error(f"CloudWatch Metric Streams operation failed: {str(e)}")
            raise
    
    async def _delete_metric_stream(
        self,
        ctx: Context,
        name: str,
    ) -> Dict[str, str]:
        """Deletes the specified metric stream."""
        try:
            return await self.metric_stream_service.delete_metric_stream(
                name=name,
            )
        except Exception as e:
            logger.error(f"Error in delete_metric_stream: {str(e)}")
            await ctx.error(f"Failed to delete metric stream: {str(e)}")
            raise
    
    async def _get_metric_stream(
        self,
        ctx: Context,
        name: str,
    ) -> Dict[str, Any]:
        """Gets details about a specific metric stream."""
        try:
            return await self.metric_stream_service.get_metric_stream(
                name=name,
            )
        except Exception as e:
            logger.error(f"Error in get_metric_stream: {str(e)}")
            await ctx.error(f"Failed to get metric stream: {str(e)}")
            raise
    
    async def _list_metric_streams(
        self,
        ctx: Context,
        next_token: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Lists metric streams in your AWS account."""
        try:
            return await self.metric_stream_service.list_metric_streams(
                next_token=next_token,
                max_results=max_results,
            )
        except Exception as e:
            logger.error(f"Error in list_metric_streams: {str(e)}")
            await ctx.error(f"Failed to list metric streams: {str(e)}")
            raise
    
    async def _put_metric_stream(
        self,
        ctx: Context,
        name: str,
        firehose_arn: str,
        role_arn: str,
        output_format: str,
        include_filters: Optional[List[Dict]] = None,
        exclude_filters: Optional[List[Dict]] = None,
        statistics_configurations: Optional[List[Dict]] = None,
        include_linked_accounts_metrics: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Creates or updates a metric stream."""
        try:
            return await self.metric_stream_service.put_metric_stream(
                name=name,
                firehose_arn=firehose_arn,
                role_arn=role_arn,
                output_format=output_format,
                include_filters=include_filters,
                exclude_filters=exclude_filters,
                statistics_configurations=statistics_configurations,
                include_linked_accounts_metrics=include_linked_accounts_metrics,
            )
        except Exception as e:
            logger.error(f"Error in put_metric_stream: {str(e)}")
            await ctx.error(f"Failed to put metric stream: {str(e)}")
            raise
    
    async def _start_metric_streams(
        self,
        ctx: Context,
        names: List[str],
    ) -> Dict[str, str]:
        """Starts the specified metric streams."""
        try:
            return await self.metric_stream_service.start_metric_streams(
                names=names,
            )
        except Exception as e:
            logger.error(f"Error in start_metric_streams: {str(e)}")
            await ctx.error(f"Failed to start metric streams: {str(e)}")
            raise
    
    async def _stop_metric_streams(
        self,
        ctx: Context,
        names: List[str],
    ) -> Dict[str, str]:
        """Stops the specified metric streams."""
        try:
            return await self.metric_stream_service.stop_metric_streams(
                names=names,
            )
        except Exception as e:
            logger.error(f"Error in stop_metric_streams: {str(e)}")
            await ctx.error(f"Failed to stop metric streams: {str(e)}")
            raise
    
    def register(self, mcp_server):
        """Register the CloudWatch Metric Streams tool with the MCP server.
        
        Args:
            mcp_server: The MCP server to register the tool with.
        """
        mcp_server.tool(
            name='cloudwatch_metric_streams',
            description="""
            Comprehensive tool for working with CloudWatch Metric Streams. Supports:
            
            - Creating and updating metric streams
            - Listing and retrieving metric stream details
            - Starting and stopping metric streams
            - Deleting metric streams
            
            Use this tool to manage CloudWatch Metric Streams for real-time metrics delivery to destinations like Amazon S3.
            """
        )(self.cloudwatch_metric_streams)