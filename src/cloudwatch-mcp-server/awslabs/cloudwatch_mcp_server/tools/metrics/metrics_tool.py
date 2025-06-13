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

"""CloudWatch Metrics tool implementation."""

from enum import Enum
from typing import Dict, List, Optional, Any, Union
from loguru import logger
from mcp.server.fastmcp import Context

from awslabs.cloudwatch_mcp_server.services.metric_service import MetricService
from awslabs.cloudwatch_mcp_server.services.client_factory import ClientFactory
from awslabs.cloudwatch_mcp_server.models import MetricList, MetricData, MetricStatistics


class MetricsOperation(str, Enum):
    """Enum for CloudWatch Metrics operations."""
    LIST_METRICS = "list_metrics"
    GET_METRIC_DATA = "get_metric_data"
    GET_METRIC_STATISTICS = "get_metric_statistics"
    PUT_METRIC_DATA = "put_metric_data"
    GET_METRIC_WIDGET_IMAGE = "get_metric_widget_image"


class MetricsTool:
    """Tool for working with CloudWatch Metrics."""
    
    def __init__(self, region_name: str = "us-east-1"):
        """Initialize the CloudWatch Metrics tool.
        
        Args:
            region_name: AWS region name.
        """
        self.region_name = region_name
        cloudwatch_client = ClientFactory.get_cloudwatch_client(region_name=region_name)
        self.metric_service = MetricService(cloudwatch_client)
    
    async def cloudwatch_metrics(
        self,
        ctx: Context,
        operation: MetricsOperation,
        # Parameters for list_metrics
        namespace: Optional[str] = None,
        metric_name: Optional[str] = None,
        dimensions: Optional[List[Dict[str, str]]] = None,
        max_items: Optional[int] = None,
        # Parameters for get_metric_data
        metric_data_queries: Optional[List[Dict]] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        scan_by: Optional[str] = None,
        max_datapoints: Optional[int] = None,
        # Parameters for get_metric_statistics
        period: Optional[int] = None,
        statistics: Optional[List[str]] = None,
        unit: Optional[str] = None,
        # Parameters for put_metric_data
        metric_data: Optional[List[Dict]] = None,
        # Parameters for get_metric_widget_image
        metric_widget: Optional[Union[str, Dict[str, Any]]] = None,
        output_format: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Perform CloudWatch Metrics operations.
        
        Args:
            ctx: The MCP context.
            operation: The operation to perform.
            
            # Parameters for list_metrics
            namespace: The namespace to filter metrics by.
            metric_name: The name of the metric to filter by.
            dimensions: The dimensions to filter by.
            max_items: The maximum number of metrics to return.
            
            # Parameters for get_metric_data
            metric_data_queries: List of metric data queries.
            start_time: ISO 8601 formatted start time.
            end_time: ISO 8601 formatted end time.
            scan_by: The order to scan the metrics in.
            max_datapoints: The maximum number of data points to return.
            
            # Parameters for get_metric_statistics
            period: The granularity, in seconds, of the returned data points.
            statistics: The statistics to retrieve.
            unit: The unit for the metric.
            
            # Parameters for put_metric_data
            metric_data: The metric data points to publish.
            
            # Parameters for get_metric_widget_image
            metric_widget: The metric widget definition.
            output_format: The format of the resulting image.
            
        Returns:
            The result of the operation, which varies based on the operation type.
        """
        try:
            if operation == MetricsOperation.LIST_METRICS:
                return await self._list_metrics(
                    ctx,
                    namespace=namespace,
                    metric_name=metric_name,
                    dimensions=dimensions,
                    max_items=max_items,
                )
            elif operation == MetricsOperation.GET_METRIC_DATA:
                if not metric_data_queries or not start_time or not end_time:
                    raise ValueError("metric_data_queries, start_time, and end_time are required for get_metric_data operation")
                
                return await self._get_metric_data(
                    ctx,
                    metric_data_queries=metric_data_queries,
                    start_time=start_time,
                    end_time=end_time,
                    scan_by=scan_by,
                    max_datapoints=max_datapoints,
                )
            elif operation == MetricsOperation.GET_METRIC_STATISTICS:
                if not namespace or not metric_name or not start_time or not end_time or not period or not statistics:
                    raise ValueError("namespace, metric_name, start_time, end_time, period, and statistics are required for get_metric_statistics operation")
                
                return await self._get_metric_statistics(
                    ctx,
                    namespace=namespace,
                    metric_name=metric_name,
                    dimensions=dimensions,
                    start_time=start_time,
                    end_time=end_time,
                    period=period,
                    statistics=statistics,
                    unit=unit,
                )
            elif operation == MetricsOperation.PUT_METRIC_DATA:
                if not namespace or not metric_data:
                    raise ValueError("namespace and metric_data are required for put_metric_data operation")
                
                return await self._put_metric_data(
                    ctx,
                    namespace=namespace,
                    metric_data=metric_data,
                )
            elif operation == MetricsOperation.GET_METRIC_WIDGET_IMAGE:
                if not metric_widget:
                    raise ValueError("metric_widget is required for get_metric_widget_image operation")
                
                return await self._get_metric_widget_image(
                    ctx,
                    metric_widget=metric_widget,
                    output_format=output_format,
                )
            else:
                raise ValueError(f"Unsupported operation: {operation}")
        except Exception as e:
            logger.error(f"Error in cloudwatch_metrics tool: {str(e)}")
            await ctx.error(f"CloudWatch Metrics operation failed: {str(e)}")
            raise
    
    async def _list_metrics(
        self,
        ctx: Context,
        namespace: Optional[str] = None,
        metric_name: Optional[str] = None,
        dimensions: Optional[List[Dict[str, str]]] = None,
        max_items: Optional[int] = None,
    ) -> MetricList:
        """Lists CloudWatch metrics based on the specified filters."""
        try:
            return await self.metric_service.list_metrics(
                namespace=namespace,
                metric_name=metric_name,
                dimensions=dimensions,
                max_items=max_items,
            )
        except Exception as e:
            logger.error(f"Error in list_metrics: {str(e)}")
            await ctx.error(f"Failed to list metrics: {str(e)}")
            raise
    
    async def _get_metric_data(
        self,
        ctx: Context,
        metric_data_queries: List[Dict],
        start_time: str,
        end_time: str,
        scan_by: Optional[str] = None,
        max_datapoints: Optional[int] = None,
    ) -> MetricData:
        """Retrieves CloudWatch metric data using the GetMetricData API."""
        try:
            return await self.metric_service.get_metric_data(
                metric_data_queries=metric_data_queries,
                start_time=start_time,
                end_time=end_time,
                scan_by=scan_by,
                max_datapoints=max_datapoints,
            )
        except Exception as e:
            logger.error(f"Error in get_metric_data: {str(e)}")
            await ctx.error(f"Failed to get metric data: {str(e)}")
            raise
    
    async def _get_metric_statistics(
        self,
        ctx: Context,
        namespace: str,
        metric_name: str,
        start_time: str,
        end_time: str,
        period: int,
        statistics: List[str],
        dimensions: Optional[List[Dict[str, str]]] = None,
        unit: Optional[str] = None,
    ) -> List[MetricStatistics]:
        """Retrieves statistics for a specified CloudWatch metric."""
        try:
            return await self.metric_service.get_metric_statistics(
                namespace=namespace,
                metric_name=metric_name,
                dimensions=dimensions,
                start_time=start_time,
                end_time=end_time,
                period=period,
                statistics=statistics,
                unit=unit,
            )
        except Exception as e:
            logger.error(f"Error in get_metric_statistics: {str(e)}")
            await ctx.error(f"Failed to get metric statistics: {str(e)}")
            raise
    
    async def _put_metric_data(
        self,
        ctx: Context,
        namespace: str,
        metric_data: List[Dict],
    ) -> Dict[str, str]:
        """Publishes metric data points to Amazon CloudWatch."""
        try:
            return await self.metric_service.put_metric_data(
                namespace=namespace,
                metric_data=metric_data,
            )
        except Exception as e:
            logger.error(f"Error in put_metric_data: {str(e)}")
            await ctx.error(f"Failed to put metric data: {str(e)}")
            raise
    
    async def _get_metric_widget_image(
        self,
        ctx: Context,
        metric_widget: Union[str, Dict[str, Any]],
        output_format: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Gets a snapshot graph of one or more CloudWatch metrics as a bitmap image."""
        try:
            return await self.metric_service.get_metric_widget_image(
                metric_widget=metric_widget,
                output_format=output_format,
            )
        except Exception as e:
            logger.error(f"Error in get_metric_widget_image: {str(e)}")
            await ctx.error(f"Failed to get metric widget image: {str(e)}")
            raise
    
    def register(self, mcp_server):
        """Register the CloudWatch Metrics tool with the MCP server.
        
        Args:
            mcp_server: The MCP server to register the tool with.
        """
        mcp_server.tool(
            name='cloudwatch_metrics',
            description="""
            Comprehensive tool for working with CloudWatch Metrics. Supports:
            
            - Listing available metrics in your AWS account
            - Retrieving metric data for analysis and visualization
            - Getting statistical data for specific metrics
            - Publishing custom metric data to CloudWatch
            - Generating metric visualizations as images
            
            Use this tool to monitor your AWS resources and applications in real-time.
            """
        )(self.cloudwatch_metrics)