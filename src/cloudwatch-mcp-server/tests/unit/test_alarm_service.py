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

"""Unit tests for the CloudWatch Alarm service."""

import datetime
import pytest
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError

from awslabs.cloudwatch_mcp_server.services.alarm_service import AlarmService


@pytest.fixture
def mock_cloudwatch_client():
    """Create a mock CloudWatch client."""
    mock_client = MagicMock()
    return mock_client


@pytest.fixture
def alarm_service(mock_cloudwatch_client):
    """Create an AlarmService instance with a mock client."""
    return AlarmService(mock_cloudwatch_client)


class TestAlarmService:
    """Tests for the AlarmService class."""

    async def test_describe_alarms_success(self, alarm_service, mock_cloudwatch_client):
        """Test successful describe_alarms call."""
        # Setup mock response
        mock_cloudwatch_client.describe_alarms.return_value = {
            'MetricAlarms': [
                {
                    'AlarmName': 'TestAlarm',
                    'AlarmArn': 'arn:aws:cloudwatch:us-east-1:123456789012:alarm:TestAlarm',
                    'StateValue': 'OK',
                    'StateReason': 'Threshold Crossed',
                    'MetricName': 'CPUUtilization',
                    'Namespace': 'AWS/EC2',
                    'Statistic': 'Average',
                    'Dimensions': [
                        {'Name': 'InstanceId', 'Value': 'i-1234567890abcdef0'}
                    ],
                    'Period': 300,
                    'Threshold': 80.0,
                    'ComparisonOperator': 'GreaterThanThreshold',
                }
            ],
            'CompositeAlarms': [],
            'NextToken': None
        }
        
        # Call the service method
        result = await alarm_service.describe_alarms(
            alarm_names=['TestAlarm']
        )
        
        # Verify the result
        assert len(result['metricAlarms']) == 1
        assert result['metricAlarms'][0]['alarmName'] == 'TestAlarm'
        assert result['metricAlarms'][0]['stateValue'] == 'OK'
        assert result['metricAlarms'][0]['metricName'] == 'CPUUtilization'
        
        # Verify the client was called correctly
        mock_cloudwatch_client.describe_alarms.assert_called_once_with(
            AlarmNames=['TestAlarm']
        )

    async def test_put_metric_alarm_success(self, alarm_service, mock_cloudwatch_client):
        """Test successful put_metric_alarm call."""
        # Setup mock response
        mock_cloudwatch_client.put_metric_alarm.return_value = {}
        
        # Call the service method
        result = await alarm_service.put_metric_alarm(
            alarm_name='TestAlarm',
            comparison_operator='GreaterThanThreshold',
            evaluation_periods=1,
            metric_name='CPUUtilization',
            namespace='AWS/EC2',
            period=300,
            statistic='Average',
            threshold=80.0
        )
        
        # Verify the result
        assert result['status'] == 'Successfully created or updated metric alarm: TestAlarm'
        
        # Verify the client was called correctly
        mock_cloudwatch_client.put_metric_alarm.assert_called_once()

    async def test_delete_alarms_success(self, alarm_service, mock_cloudwatch_client):
        """Test successful delete_alarms call."""
        # Setup mock response
        mock_cloudwatch_client.delete_alarms.return_value = {}
        
        # Call the service method
        result = await alarm_service.delete_alarms(
            alarm_names=['TestAlarm1', 'TestAlarm2']
        )
        
        # Verify the result
        assert result['status'] == 'Successfully deleted 2 alarms'
        
        # Verify the client was called correctly
        mock_cloudwatch_client.delete_alarms.assert_called_once_with(
            AlarmNames=['TestAlarm1', 'TestAlarm2']
        )

    async def test_enable_alarm_actions_success(self, alarm_service, mock_cloudwatch_client):
        """Test successful enable_alarm_actions call."""
        # Setup mock response
        mock_cloudwatch_client.enable_alarm_actions.return_value = {}
        
        # Call the service method
        result = await alarm_service.enable_alarm_actions(
            alarm_names=['TestAlarm1', 'TestAlarm2']
        )
        
        # Verify the result
        assert result['status'] == 'Successfully enabled actions for 2 alarms'
        
        # Verify the client was called correctly
        mock_cloudwatch_client.enable_alarm_actions.assert_called_once_with(
            AlarmNames=['TestAlarm1', 'TestAlarm2']
        )