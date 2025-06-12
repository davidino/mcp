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

"""CloudWatch Anomaly Detector service implementation."""

from typing import Dict, List, Optional, Any
from botocore.exceptions import ClientError
from loguru import logger

from awslabs.cloudwatch_mcp_server.common import remove_null_values


class AnomalyDetectorService:
    """Service for CloudWatch Anomaly Detector operations."""
    
    def __init__(self, cloudwatch_client):
        """Initialize the anomaly detector service with a CloudWatch client."""
        self.cloudwatch_client = cloudwatch_client
    
    async def delete_anomaly_detector(
        self,
        namespace: str,
        metric_name: str,
        dimensions: Optional[List[Dict[str, str]]] = None,
        stat: Optional[str] = None,
        single_metric_anomaly_detector: Optional[Dict] = None,
        metric_math_anomaly_detector: Optional[Dict] = None,
    ) -> Dict[str, str]:
        """Deletes the specified anomaly detection model."""
        try:
            kwargs = {
                'Namespace': namespace,
                'MetricName': metric_name,
                'Dimensions': dimensions,
                'Stat': stat,
                'SingleMetricAnomalyDetector': single_metric_anomaly_detector,
                'MetricMathAnomalyDetector': metric_math_anomaly_detector,
            }
            self.cloudwatch_client.delete_anomaly_detector(**remove_null_values(kwargs))
            logger.info(f'Successfully deleted anomaly detector for {namespace}:{metric_name}')
            return {"status": f"Successfully deleted anomaly detector for {namespace}:{metric_name}"}
        except ClientError as e:
            logger.error(f"ClientError in delete_anomaly_detector: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in delete_anomaly_detector: {e}")
            raise
    
    async def describe_anomaly_detectors(
        self,
        namespace: Optional[str] = None,
        metric_name: Optional[str] = None,
        dimensions: Optional[List[Dict[str, str]]] = None,
        stat: Optional[str] = None,
        next_token: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Lists the anomaly detection models that you have created."""
        try:
            kwargs = {
                'Namespace': namespace,
                'MetricName': metric_name,
                'Dimensions': dimensions,
                'Stat': stat,
                'NextToken': next_token,
                'MaxResults': max_results,
            }
            response = self.cloudwatch_client.describe_anomaly_detectors(**remove_null_values(kwargs))
            return {
                "anomalyDetectors": response.get('AnomalyDetectors', []),
                "nextToken": response.get('NextToken')
            }
        except ClientError as e:
            logger.error(f"ClientError in describe_anomaly_detectors: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in describe_anomaly_detectors: {e}")
            raise
    
    async def put_anomaly_detector(
        self,
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
            kwargs = {
                'Namespace': namespace,
                'MetricName': metric_name,
                'Dimensions': dimensions,
                'Stat': stat,
                'Configuration': configuration,
                'SingleMetricAnomalyDetector': single_metric_anomaly_detector,
                'MetricMathAnomalyDetector': metric_math_anomaly_detector,
            }
            self.cloudwatch_client.put_anomaly_detector(**remove_null_values(kwargs))
            logger.info(f'Successfully created or updated anomaly detector for {namespace}:{metric_name}')
            return {"status": f"Successfully created or updated anomaly detector for {namespace}:{metric_name}"}
        except ClientError as e:
            logger.error(f"ClientError in put_anomaly_detector: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in put_anomaly_detector: {e}")
            raise