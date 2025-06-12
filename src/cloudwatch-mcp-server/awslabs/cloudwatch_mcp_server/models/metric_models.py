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

"""CloudWatch Metric models."""

import datetime
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any


class Dimension(BaseModel):
    """Represents a CloudWatch metric dimension."""
    
    name: str = Field(..., description='The name of the dimension')
    value: str = Field(..., description='The value of the dimension')


class Metric(BaseModel):
    """Represents a CloudWatch metric."""
    
    namespace: str = Field(..., description='The namespace of the metric')
    metricName: str = Field(..., description='The name of the metric')
    dimensions: List[Dimension] = Field(default_factory=list, description='The dimensions of the metric')


class MetricList(BaseModel):
    """Represents a list of CloudWatch metrics."""
    
    metrics: List[Metric] = Field(..., description='List of metrics')


class MetricDataResult(BaseModel):
    """Represents the result of a GetMetricData API call for a single metric."""
    
    id: str = Field(..., description='The ID of the metric data query')
    label: Optional[str] = Field(None, description='The label of the metric')
    statusCode: str = Field(..., description='The status code of the metric data query')
    timestamps: List[datetime.datetime] = Field(default_factory=list, description='The timestamps of the data points')
    values: List[float] = Field(default_factory=list, description='The values of the data points')
    messages: Optional[List[str]] = Field(None, description='The messages associated with the metric data query')


class MetricData(BaseModel):
    """Represents the result of a GetMetricData API call."""
    
    metricDataResults: List[MetricDataResult] = Field(..., description='The results of the metric data queries')
    nextToken: Optional[str] = Field(None, description='The token for the next set of results')
    messages: Optional[List[str]] = Field(None, description='The messages associated with the metric data query')


class MetricStatistics(BaseModel):
    """Represents the statistics for a CloudWatch metric."""
    
    timestamp: datetime.datetime = Field(..., description='The timestamp of the data point')
    sampleCount: Optional[float] = Field(None, description='The number of samples used for the statistic')
    average: Optional[float] = Field(None, description='The average of the metric values')
    sum: Optional[float] = Field(None, description='The sum of the metric values')
    minimum: Optional[float] = Field(None, description='The minimum metric value')
    maximum: Optional[float] = Field(None, description='The maximum metric value')