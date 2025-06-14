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

"""CloudWatch Anomaly Detectors tool implementation."""

from enum import Enum
from typing import Dict, List, Optional, Any
from loguru import logger
from mcp.server.fastmcp import Context

from awslabs.cloudwatch_mcp_server.services.anomaly_detector_service import AnomalyDetectorService
from awslabs.cloudwatch_mcp_server.services.client_factory import ClientFactory


class AnomalyDetectorsOperation(str, Enum):
    """Enum for CloudWatch Anomaly Detectors operations."""
    DELETE_ANOMALY_DETECTOR = "delete_anomaly_detector"
    DESCRIBE_ANOMALY_DETECTORS = "describe_anomaly_detectors"
    PUT_ANOMALY_DETECTOR = "put_anomaly_detector"


class AnomalyDetectorsTool:
    """Tool for working with CloudWatch Anomaly Detectors."""
    
    def __init__(self, region_name: str = "us-east-1"):
        """Initialize the CloudWatch Anomaly Detectors tool.
        
        Args:
            region_name: AWS region name.
        """
        self.region_name = region_name
        cloudwatch_client = ClientFactory.get_cloudwatch_client(region_name=region_name)
        self.anomaly_detector_service = AnomalyDetectorService(cloudwatch_client)
    
    async def cloudwatch_anomaly_detectors(
        self,
        ctx: Context,
        operation: AnomalyDetectorsOperation,
        # Common parameters
        namespace: Optional[str] = None,
        metric_name: Optional[str] = None,
        dimensions: Optional[List[Dict[str, str]]] = None,
        stat: Optional[str] = None,
        # Parameters for put_anomaly_detector
        configuration: Optional[Dict] = None,
        single_metric_anomaly_detector: Optional[Dict] = None,
        metric_math_anomaly_detector: Optional[Dict] = None,
        # Pagination parameters
        next_token: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Perform CloudWatch Anomaly Detectors operations.
        
        Args:
            ctx: The MCP context.
            operation: The operation to perform.
            
            # Common parameters
            namespace: The namespace of the metric.
            metric_name: The name of the metric.
            dimensions: The dimensions of the metric.
            stat: The statistic of the metric.
            
            # Parameters for put_anomaly_detector
            configuration: The configuration for the anomaly detection model.
            single_metric_anomaly_detector: A single metric anomaly detector.
            metric_math_anomaly_detector: A metric math anomaly detector.
            
            # Pagination parameters
            next_token: The token for the next set of results.
            max_results: The maximum number of results to return.
            
        Returns:
            The result of the operation, which varies based on the operation type.
        """
        try:
            if operation == AnomalyDetectorsOperation.DELETE_ANOMALY_DETECTOR:
                if not namespace or not metric_name:
                    raise ValueError("namespace and metric_name are required for delete_anomaly_detector operation")
                
                return await self._delete_anomaly_detector(
                    ctx,
                    namespace=namespace,
                    metric_name=metric_name,
                    dimensions=dimensions,
                    stat=stat,
                    single_metric_anomaly_detector=single_metric_anomaly_detector,
                    metric_math_anomaly_detector=metric_math_anomaly_detector,
                )
            if operation == AnomalyDetectorsOperation.DESCRIBE_ANOMALY_DETECTORS:
                return await self._describe_anomaly_detectors(
                    ctx,
                    namespace=namespace,
                    metric_name=metric_name,
                    dimensions=dimensions,
                    stat=stat,
                    next_token=next_token,
                    max_results=max_results,
                )
            if operation == AnomalyDetectorsOperation.PUT_ANOMALY_DETECTOR:
                if not namespace or not metric_name:
                    raise ValueError("namespace and metric_name are required for put_anomaly_detector operation")
                
                return await self._put_anomaly_detector(
                    ctx,
                    namespace=namespace,
                    metric_name=metric_name,
                    dimensions=dimensions,
                    stat=stat,
                    configuration=configuration,
                    single_metric_anomaly_detector=single_metric_anomaly_detector,
                    metric_math_anomaly_detector=metric_math_anomaly_detector,
                )
            else:
                raise ValueError(f"Unsupported operation: {operation}")
        except Exception as e:
            logger.error(f"Error in cloudwatch_anomaly_detectors tool: {str(e)}")
            await ctx.error(f"CloudWatch Anomaly Detectors operation failed: {str(e)}")
            raise
    
    async def _delete_anomaly_detector(
        self,
        ctx: Context,
        namespace: str,
        metric_name: str,
        dimensions: Optional[List[Dict[str, str]]] = None,
        stat: Optional[str] = None,
        single_metric_anomaly_detector: Optional[Dict] = None,
        metric_math_anomaly_detector: Optional[Dict] = None,
    ) -> Dict[str, str]:
        """Deletes the specified anomaly detection model."""
        try:
            return await self.anomaly_detector_service.delete_anomaly_detector(
                namespace=namespace,
                metric_name=metric_name,
                dimensions=dimensions,
                stat=stat,
                single_metric_anomaly_detector=single_metric_anomaly_detector,
                metric_math_anomaly_detector=metric_math_anomaly_detector,
            )
        except Exception as e:
            logger.error(f"Error in delete_anomaly_detector: {str(e)}")
            await ctx.error(f"Failed to delete anomaly detector: {str(e)}")
            raise
    
    async def _describe_anomaly_detectors(
        self,
        ctx: Context,
        namespace: Optional[str] = None,
        metric_name: Optional[str] = None,
        dimensions: Optional[List[Dict[str, str]]] = None,
        stat: Optional[str] = None,
        next_token: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Lists the anomaly detection models that you have created."""
        try:
            return await self.anomaly_detector_service.describe_anomaly_detectors(
                namespace=namespace,
                metric_name=metric_name,
                dimensions=dimensions,
                stat=stat,
                next_token=next_token,
                max_results=max_results,
            )
        except Exception as e:
            logger.error(f"Error in describe_anomaly_detectors: {str(e)}")
            await ctx.error(f"Failed to describe anomaly detectors: {str(e)}")
            raise
    
    async def _put_anomaly_detector(
        self,
        ctx: Context,
        namespace: str,
        metric_name: str,
        dimensions: Optional[List[Dict[str, str]]] = None,
        stat: Optional[str] = None,
        configuration: Optional[Dict] = None,
        single_metric_anomaly_detector: Optional[Dict] = None,
        metric_math_anomaly_detector: Optional[Dict] = None,
    ) -> Dict[str, str]:
        """Creates or updates an anomaly detection model for a CloudWatch metric."""
        try:
            return await self.anomaly_detector_service.put_anomaly_detector(
                namespace=namespace,
                metric_name=metric_name,
                dimensions=dimensions,
                stat=stat,
                configuration=configuration,
                single_metric_anomaly_detector=single_metric_anomaly_detector,
                metric_math_anomaly_detector=metric_math_anomaly_detector,
            )
        except Exception as e:
            logger.error(f"Error in put_anomaly_detector: {str(e)}")
            await ctx.error(f"Failed to put anomaly detector: {str(e)}")
            raise
    
    def register(self, mcp_server):
        """Register the CloudWatch Anomaly Detectors tool with the MCP server.
        
        Args:
            mcp_server: The MCP server to register the tool with.
        """
        mcp_server.tool(
            name='cloudwatch_anomaly_detectors',
            description="""
            Tool for working with CloudWatch Anomaly Detectors. Supports:
            
            - Creating and updating anomaly detection models
            - Listing existing anomaly detectors
            - Deleting anomaly detectors
            
            Use this tool to detect unusual behavior in your CloudWatch metrics.
            """
        )(self.cloudwatch_anomaly_detectors)