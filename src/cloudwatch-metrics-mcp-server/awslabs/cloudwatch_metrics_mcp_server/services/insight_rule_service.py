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

"""CloudWatch Insight Rule service implementation."""

import datetime
from typing import Dict, List, Optional, Any
from botocore.exceptions import ClientError
from loguru import logger

from awslabs.cloudwatch_metrics_mcp_server.common import remove_null_values


class InsightRuleService:
    """Service for CloudWatch Insight Rule operations."""
    
    def __init__(self, cloudwatch_client):
        """Initialize the insight rule service with a CloudWatch client."""
        self.cloudwatch_client = cloudwatch_client
    
    async def delete_insight_rules(
        self,
        rule_names: List[str],
    ) -> Dict[str, Any]:
        """Deletes the specified Contributor Insights rules."""
        try:
            response = self.cloudwatch_client.delete_insight_rules(
                RuleNames=rule_names
            )
            
            failures = response.get('Failures', [])
            if failures:
                failure_messages = [f"{f.get('FailureResource')}: {f.get('ExceptionType')} - {f.get('ErrorMessage')}" for f in failures]
                return {
                    "status": f"Deleted {len(rule_names) - len(failures)} rules, with {len(failures)} failures",
                    "failures": failure_messages
                }
            
            logger.info(f'Successfully deleted {len(rule_names)} insight rules')
            return {"status": f"Successfully deleted {len(rule_names)} insight rules"}
        except ClientError as e:
            logger.error(f"ClientError in delete_insight_rules: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in delete_insight_rules: {e}")
            raise
    
    async def describe_insight_rules(
        self,
        next_token: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Returns a list of all Contributor Insights rules in your account."""
        try:
            kwargs = {
                'NextToken': next_token,
                'MaxResults': max_results,
            }
            
            response = self.cloudwatch_client.describe_insight_rules(**remove_null_values(kwargs))
            
            return {
                "insightRules": response.get('InsightRules', []),
                "nextToken": response.get('NextToken')
            }
        except ClientError as e:
            logger.error(f"ClientError in describe_insight_rules: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in describe_insight_rules: {e}")
            raise
    
    async def disable_insight_rules(
        self,
        rule_names: List[str],
    ) -> Dict[str, Any]:
        """Disables the specified Contributor Insights rules."""
        try:
            response = self.cloudwatch_client.disable_insight_rules(
                RuleNames=rule_names
            )
            
            failures = response.get('Failures', [])
            if failures:
                failure_messages = [f"{f.get('FailureResource')}: {f.get('ExceptionType')} - {f.get('ErrorMessage')}" for f in failures]
                return {
                    "status": f"Disabled {len(rule_names) - len(failures)} rules, with {len(failures)} failures",
                    "failures": failure_messages
                }
            
            logger.info(f'Successfully disabled {len(rule_names)} insight rules')
            return {"status": f"Successfully disabled {len(rule_names)} insight rules"}
        except ClientError as e:
            logger.error(f"ClientError in disable_insight_rules: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in disable_insight_rules: {e}")
            raise
    
    async def enable_insight_rules(
        self,
        rule_names: List[str],
    ) -> Dict[str, Any]:
        """Enables the specified Contributor Insights rules."""
        try:
            response = self.cloudwatch_client.enable_insight_rules(
                RuleNames=rule_names
            )
            
            failures = response.get('Failures', [])
            if failures:
                failure_messages = [f"{f.get('FailureResource')}: {f.get('ExceptionType')} - {f.get('ErrorMessage')}" for f in failures]
                return {
                    "status": f"Enabled {len(rule_names) - len(failures)} rules, with {len(failures)} failures",
                    "failures": failure_messages
                }
            
            logger.info(f'Successfully enabled {len(rule_names)} insight rules')
            return {"status": f"Successfully enabled {len(rule_names)} insight rules"}
        except ClientError as e:
            logger.error(f"ClientError in enable_insight_rules: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in enable_insight_rules: {e}")
            raise
    
    async def get_insight_rule_report(
        self,
        rule_name: str,
        start_time: str,
        end_time: str,
        period: int,
        max_contributor_count: Optional[int] = None,
        metrics: Optional[List[str]] = None,
        order_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Returns data about the contributors for the specified rule."""
        try:
            kwargs = {
                'RuleName': rule_name,
                'StartTime': datetime.datetime.fromisoformat(start_time),
                'EndTime': datetime.datetime.fromisoformat(end_time),
                'Period': period,
                'MaxContributorCount': max_contributor_count,
                'Metrics': metrics,
                'OrderBy': order_by,
            }
            
            response = self.cloudwatch_client.get_insight_rule_report(**remove_null_values(kwargs))
            
            return {
                "keyLabels": response.get('KeyLabels', []),
                "aggregationStatistic": response.get('AggregationStatistic'),
                "aggregateValue": response.get('AggregateValue'),
                "approximateUniqueCount": response.get('ApproximateUniqueCount'),
                "contributors": response.get('Contributors', []),
                "metricDatapoints": response.get('MetricDatapoints', [])
            }
        except ClientError as e:
            logger.error(f"ClientError in get_insight_rule_report: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in get_insight_rule_report: {e}")
            raise
    
    async def list_managed_insight_rules(
        self,
        resource_arn: str,
        next_token: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Returns a list of managed Contributor Insights rules for a specific AWS resource."""
        try:
            kwargs = {
                'ResourceARN': resource_arn,
                'NextToken': next_token,
                'MaxResults': max_results,
            }
            
            response = self.cloudwatch_client.list_managed_insight_rules(**remove_null_values(kwargs))
            
            return {
                "managedRules": response.get('ManagedRules', []),
                "nextToken": response.get('NextToken')
            }
        except ClientError as e:
            logger.error(f"ClientError in list_managed_insight_rules: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in list_managed_insight_rules: {e}")
            raise
    
    async def put_insight_rule(
        self,
        rule_name: str,
        rule_definition: str,
        rule_state: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Creates a Contributor Insights rule."""
        try:
            kwargs = {
                'RuleName': rule_name,
                'RuleDefinition': rule_definition,
                'RuleState': rule_state,
                'Tags': tags,
            }
            
            response = self.cloudwatch_client.put_insight_rule(**remove_null_values(kwargs))
            
            logger.info(f'Successfully created or updated insight rule: {rule_name}')
            return {
                "status": f"Successfully created or updated insight rule: {rule_name}",
                "ruleArn": response.get('RuleArn')
            }
        except ClientError as e:
            logger.error(f"ClientError in put_insight_rule: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in put_insight_rule: {e}")
            raise
    
    async def put_managed_insight_rules(
        self,
        managed_rules: List[Dict],
    ) -> Dict[str, Any]:
        """Creates managed Contributor Insights rules for a specified AWS resource."""
        try:
            response = self.cloudwatch_client.put_managed_insight_rules(
                ManagedRules=managed_rules
            )
            
            failures = response.get('Failures', [])
            if failures:
                failure_messages = [f"{f.get('FailureResource')}: {f.get('ExceptionType')} - {f.get('ErrorMessage')}" for f in failures]
                return {
                    "status": f"Created {len(managed_rules) - len(failures)} rules, with {len(failures)} failures",
                    "failures": failure_messages
                }
            
            logger.info(f'Successfully created {len(managed_rules)} managed insight rules')
            return {"status": f"Successfully created {len(managed_rules)} managed insight rules"}
        except ClientError as e:
            logger.error(f"ClientError in put_managed_insight_rules: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in put_managed_insight_rules: {e}")
            raise