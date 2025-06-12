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

"""CloudWatch Alarm service implementation."""

import datetime
from typing import Dict, List, Optional, Any, Union
from botocore.exceptions import ClientError
from loguru import logger

from awslabs.cloudwatch_mcp_server.common import remove_null_values


class AlarmService:
    """Service for CloudWatch Alarm operations."""
    
    def __init__(self, cloudwatch_client):
        """Initialize the alarm service with a CloudWatch client."""
        self.cloudwatch_client = cloudwatch_client
    
    async def describe_alarm_history(
        self,
        alarm_name: Optional[str] = None,
        alarm_types: Optional[List[str]] = None,
        history_item_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        max_records: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Retrieves the history for the specified alarm."""
        try:
            kwargs = {
                'AlarmName': alarm_name,
                'AlarmTypes': alarm_types,
                'HistoryItemType': history_item_type,
                'StartDate': datetime.datetime.fromisoformat(start_date) if start_date else None,
                'EndDate': datetime.datetime.fromisoformat(end_date) if end_date else None,
                'MaxRecords': max_records,
                'NextToken': next_token,
            }
            
            response = self.cloudwatch_client.describe_alarm_history(**remove_null_values(kwargs))
            
            # Convert to a simpler format
            history_items = []
            for item in response.get('AlarmHistoryItems', []):
                history_items.append({
                    'alarmName': item.get('AlarmName'),
                    'timestamp': item.get('Timestamp').isoformat() if hasattr(item.get('Timestamp'), 'isoformat') else str(item.get('Timestamp')),
                    'historyItemType': item.get('HistoryItemType'),
                    'historySummary': item.get('HistorySummary'),
                    'historyData': item.get('HistoryData'),
                })
            
            return {
                'alarmHistoryItems': history_items,
                'nextToken': response.get('NextToken')
            }
        
        except ClientError as e:
            logger.error(f"ClientError in describe_alarm_history: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in describe_alarm_history: {e}")
            raise
    
    async def describe_alarms(
        self,
        alarm_names: Optional[List[str]] = None,
        alarm_name_prefix: Optional[str] = None,
        alarm_types: Optional[List[str]] = None,
        state_value: Optional[str] = None,
        action_prefix: Optional[str] = None,
        max_records: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Retrieves information about the specified alarms."""
        try:
            kwargs = {
                'AlarmNames': alarm_names,
                'AlarmNamePrefix': alarm_name_prefix,
                'AlarmTypes': alarm_types,
                'StateValue': state_value,
                'ActionPrefix': action_prefix,
                'MaxRecords': max_records,
                'NextToken': next_token,
            }
            
            response = self.cloudwatch_client.describe_alarms(**remove_null_values(kwargs))
            
            # Convert to a simpler format
            metric_alarms = []
            for alarm in response.get('MetricAlarms', []):
                metric_alarms.append({
                    'alarmName': alarm.get('AlarmName'),
                    'alarmArn': alarm.get('AlarmArn'),
                    'stateValue': alarm.get('StateValue'),
                    'stateReason': alarm.get('StateReason'),
                    'metricName': alarm.get('MetricName'),
                    'namespace': alarm.get('Namespace'),
                    'statistic': alarm.get('Statistic'),
                    'dimensions': alarm.get('Dimensions'),
                    'period': alarm.get('Period'),
                    'threshold': alarm.get('Threshold'),
                    'comparisonOperator': alarm.get('ComparisonOperator'),
                })
            
            composite_alarms = []
            for alarm in response.get('CompositeAlarms', []):
                composite_alarms.append({
                    'alarmName': alarm.get('AlarmName'),
                    'alarmArn': alarm.get('AlarmArn'),
                    'stateValue': alarm.get('StateValue'),
                    'stateReason': alarm.get('StateReason'),
                    'alarmRule': alarm.get('AlarmRule'),
                })
            
            return {
                'metricAlarms': metric_alarms,
                'compositeAlarms': composite_alarms,
                'nextToken': response.get('NextToken')
            }
        
        except ClientError as e:
            logger.error(f"ClientError in describe_alarms: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in describe_alarms: {e}")
            raise
    
    async def describe_alarms_for_metric(
        self,
        namespace: str,
        metric_name: str,
        dimensions: Optional[List[Dict[str, str]]] = None,
        statistic: Optional[str] = None,
        extended_statistic: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Retrieves all alarms for a specified metric."""
        try:
            kwargs = {
                'MetricName': metric_name,
                'Namespace': namespace,
                'Dimensions': dimensions,
                'Statistic': statistic,
                'ExtendedStatistic': extended_statistic,
            }
            
            response = self.cloudwatch_client.describe_alarms_for_metric(**remove_null_values(kwargs))
            
            # Convert to a simpler format
            metric_alarms = []
            for alarm in response.get('MetricAlarms', []):
                metric_alarms.append({
                    'alarmName': alarm.get('AlarmName'),
                    'alarmArn': alarm.get('AlarmArn'),
                    'stateValue': alarm.get('StateValue'),
                    'stateReason': alarm.get('StateReason'),
                    'metricName': alarm.get('MetricName'),
                    'namespace': alarm.get('Namespace'),
                    'statistic': alarm.get('Statistic'),
                    'dimensions': alarm.get('Dimensions'),
                    'period': alarm.get('Period'),
                    'threshold': alarm.get('Threshold'),
                    'comparisonOperator': alarm.get('ComparisonOperator'),
                })
            
            return {
                'metricAlarms': metric_alarms
            }
        
        except ClientError as e:
            logger.error(f"ClientError in describe_alarms_for_metric: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in describe_alarms_for_metric: {e}")
            raise
    
    async def put_composite_alarm(
        self,
        alarm_name: str,
        alarm_rule: str,
        actions_enabled: Optional[bool] = None,
        alarm_actions: Optional[List[str]] = None,
        alarm_description: Optional[str] = None,
        insufficient_data_actions: Optional[List[str]] = None,
        ok_actions: Optional[List[str]] = None,
    ) -> Dict[str, str]:
        """Creates or updates a composite alarm."""
        try:
            kwargs = {
                'AlarmName': alarm_name,
                'AlarmRule': alarm_rule,
                'ActionsEnabled': actions_enabled,
                'AlarmActions': alarm_actions,
                'AlarmDescription': alarm_description,
                'InsufficientDataActions': insufficient_data_actions,
                'OKActions': ok_actions,
            }
            
            self.cloudwatch_client.put_composite_alarm(**remove_null_values(kwargs))
            
            logger.info(f'Successfully created or updated composite alarm: {alarm_name}')
            return {"status": f"Successfully created or updated composite alarm: {alarm_name}"}
        
        except ClientError as e:
            logger.error(f"ClientError in put_composite_alarm: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in put_composite_alarm: {e}")
            raise
    
    async def put_metric_alarm(
        self,
        alarm_name: str,
        comparison_operator: str,
        evaluation_periods: int,
        metric_name: Optional[str] = None,
        namespace: Optional[str] = None,
        period: Optional[int] = None,
        statistic: Optional[str] = None,
        threshold: Optional[float] = None,
        actions_enabled: Optional[bool] = None,
        alarm_actions: Optional[List[str]] = None,
        alarm_description: Optional[str] = None,
        dimensions: Optional[List[Dict[str, str]]] = None,
        insufficient_data_actions: Optional[List[str]] = None,
        ok_actions: Optional[List[str]] = None,
        unit: Optional[str] = None,
    ) -> Dict[str, str]:
        """Creates or updates a metric alarm."""
        try:
            kwargs = {
                'AlarmName': alarm_name,
                'ComparisonOperator': comparison_operator,
                'EvaluationPeriods': evaluation_periods,
                'MetricName': metric_name,
                'Namespace': namespace,
                'Period': period,
                'Statistic': statistic,
                'Threshold': threshold,
                'ActionsEnabled': actions_enabled,
                'AlarmActions': alarm_actions,
                'AlarmDescription': alarm_description,
                'Dimensions': dimensions,
                'InsufficientDataActions': insufficient_data_actions,
                'OKActions': ok_actions,
                'Unit': unit,
            }
            
            self.cloudwatch_client.put_metric_alarm(**remove_null_values(kwargs))
            
            logger.info(f'Successfully created or updated metric alarm: {alarm_name}')
            return {"status": f"Successfully created or updated metric alarm: {alarm_name}"}
        
        except ClientError as e:
            logger.error(f"ClientError in put_metric_alarm: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in put_metric_alarm: {e}")
            raise
    
    async def delete_alarms(
        self,
        alarm_names: List[str],
    ) -> Dict[str, str]:
        """Deletes the specified CloudWatch alarms."""
        try:
            self.cloudwatch_client.delete_alarms(
                AlarmNames=alarm_names
            )
            
            logger.info(f'Successfully deleted {len(alarm_names)} alarms')
            return {"status": f"Successfully deleted {len(alarm_names)} alarms"}
        
        except ClientError as e:
            logger.error(f"ClientError in delete_alarms: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in delete_alarms: {e}")
            raise
    
    async def disable_alarm_actions(
        self,
        alarm_names: List[str],
    ) -> Dict[str, str]:
        """Disables actions for the specified alarms."""
        try:
            self.cloudwatch_client.disable_alarm_actions(
                AlarmNames=alarm_names
            )
            
            logger.info(f'Successfully disabled actions for {len(alarm_names)} alarms')
            return {"status": f"Successfully disabled actions for {len(alarm_names)} alarms"}
        
        except ClientError as e:
            logger.error(f"ClientError in disable_alarm_actions: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in disable_alarm_actions: {e}")
            raise
    
    async def enable_alarm_actions(
        self,
        alarm_names: List[str],
    ) -> Dict[str, str]:
        """Enables actions for the specified alarms."""
        try:
            self.cloudwatch_client.enable_alarm_actions(
                AlarmNames=alarm_names
            )
            
            logger.info(f'Successfully enabled actions for {len(alarm_names)} alarms')
            return {"status": f"Successfully enabled actions for {len(alarm_names)} alarms"}
        
        except ClientError as e:
            logger.error(f"ClientError in enable_alarm_actions: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in enable_alarm_actions: {e}")
            raise
    
    async def set_alarm_state(
        self,
        alarm_name: str,
        state_value: str,
        state_reason: str,
        state_reason_data: Optional[str] = None,
    ) -> Dict[str, str]:
        """Temporarily sets the state of an alarm."""
        try:
            kwargs = {
                'AlarmName': alarm_name,
                'StateValue': state_value,
                'StateReason': state_reason,
                'StateReasonData': state_reason_data,
            }
            
            self.cloudwatch_client.set_alarm_state(**remove_null_values(kwargs))
            
            logger.info(f'Successfully set alarm state for {alarm_name} to {state_value}')
            return {"status": f"Successfully set alarm state for {alarm_name} to {state_value}"}
        
        except ClientError as e:
            logger.error(f"ClientError in set_alarm_state: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in set_alarm_state: {e}")
            raise