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

from awslabs.cloudwatch_metrics_mcp_server.common import epoch_s_to_utc_iso
from pydantic import BaseModel, Field, field_validator
from typing import Any, Dict, List, Optional, Union


class Dimension(BaseModel):
    """Represents a CloudWatch metric dimension."""
    
    name: str = Field(..., description='The name of the dimension')
    value: str = Field(..., description='The value of the dimension')


class Metric(BaseModel):
    """Represents a CloudWatch metric."""
    
    namespace: str = Field(..., description='The namespace of the metric')
    metricName: str = Field(..., description='The name of the metric')
    dimensions: List[Dimension] = Field(default_factory=list, description='The dimensions of the metric')


class MetricDataResult(BaseModel):
    """Represents the result of a CloudWatch metric data query."""
    
    id: str = Field(..., description='The ID of the metric data query')
    label: Optional[str] = Field(None, description='The label of the metric data')
    statusCode: str = Field(..., description='The status code of the metric data query')
    timestamps: List[str] = Field(default_factory=list, description='The timestamps of the metric data points')
    values: List[float] = Field(default_factory=list, description='The values of the metric data points')
    messages: Optional[List[Dict[str, str]]] = Field(None, description='Messages about the metric data query')
    
    @field_validator('timestamps', mode='before')
    @classmethod
    def convert_timestamps_to_iso8601(cls, v):
        """Convert timestamps from epoch seconds to ISO 8601 format."""
        if isinstance(v, list):
            result = []
            for ts in v:
                if isinstance(ts, (int, float)):
                    result.append(epoch_s_to_utc_iso(int(ts)))
                elif hasattr(ts, 'isoformat'):  # Handle datetime objects
                    result.append(ts.isoformat())
                else:
                    result.append(str(ts))  # Fallback to string conversion
            return result
        return v


class MetricDataQuery(BaseModel):
    """Represents a CloudWatch metric data query."""
    
    id: str = Field(..., description='The ID of the metric data query')
    metricStat: Optional[Dict[str, Any]] = Field(None, description='The metric and stat to query')
    expression: Optional[str] = Field(None, description='The math expression to perform on the metrics')
    label: Optional[str] = Field(None, description='The label for the metric data query')
    returnData: Optional[bool] = Field(None, description='Whether to return the data for this query')
    period: Optional[int] = Field(None, description='The period in seconds for the metric data query')


class MetricStatistics(BaseModel):
    """Represents statistics for a CloudWatch metric."""
    
    timestamp: str = Field(..., description='The timestamp for the statistics')
    sampleCount: Optional[float] = Field(None, description='The sample count statistic')
    average: Optional[float] = Field(None, description='The average statistic')
    sum: Optional[float] = Field(None, description='The sum statistic')
    minimum: Optional[float] = Field(None, description='The minimum statistic')
    maximum: Optional[float] = Field(None, description='The maximum statistic')
    
    @field_validator('timestamp', mode='before')
    @classmethod
    def convert_timestamp_to_iso8601(cls, v):
        """Convert timestamp from epoch seconds to ISO 8601 format."""
        if isinstance(v, (int, float)):
            return epoch_s_to_utc_iso(int(v))
        elif hasattr(v, 'isoformat'):  # Handle datetime objects
            return v.isoformat()
        return str(v)  # Fallback to string conversion


class MetricData(BaseModel):
    """Represents the response from a GetMetricData API call."""
    
    metricDataResults: List[MetricDataResult] = Field(..., description='The results of the metric data queries')
    nextToken: Optional[str] = Field(None, description='The token for the next set of results')
    messages: Optional[List[Dict[str, str]]] = Field(None, description='Messages about the metric data query')


class MetricList(BaseModel):
    """Represents a list of CloudWatch metrics."""
    
    metrics: List[Metric] = Field(..., description='List of metrics')
    nextToken: Optional[str] = Field(None, description='The token for the next set of results')