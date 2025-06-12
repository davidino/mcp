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

"""CloudWatch Logs service implementation."""

import asyncio
import datetime
from timeit import default_timer as timer
from typing import Dict, List, Optional, Any, Set
from botocore.exceptions import ClientError
from loguru import logger

from awslabs.cloudwatch_mcp_server.common import remove_null_values, filter_by_prefixes, clean_up_pattern
from awslabs.cloudwatch_mcp_server.models.logs_models import (
    LogGroupMetadata,
    SavedQuery,
    LogMetadata,
    AnomalyDetector,
    LogAnomaly,
    LogAnomalyResults,
    LogAnalysisResult,
    CancelQueryResult,
)


class LogsService:
    """Service for CloudWatch Logs operations."""
    
    def __init__(self, logs_client):
        """Initialize the logs service with a CloudWatch Logs client."""
        self.logs_client = logs_client
    
    async def describe_log_groups(
        self,
        account_identifiers: Optional[List[str]] = None,
        include_linked_accounts: Optional[bool] = False,
        log_group_class: Optional[str] = None,
        log_group_name_prefix: Optional[str] = None,
        max_items: Optional[int] = None,
    ) -> LogMetadata:
        """Lists AWS CloudWatch log groups and saved queries associated with them."""
        try:
            # Get log groups
            paginator = self.logs_client.get_paginator('describe_log_groups')
            kwargs = {
                'accountIdentifiers': account_identifiers,
                'includeLinkedAccounts': include_linked_accounts,
                'logGroupNamePrefix': log_group_name_prefix,
                'logGroupClass': log_group_class,
            }

            if max_items:
                kwargs['PaginationConfig'] = {'MaxItems': max_items}

            log_groups = []
            for page in paginator.paginate(**remove_null_values(kwargs)):
                log_groups.extend(page.get('logGroups', []))

            logger.info(f'Found {len(log_groups)} log groups')
            log_group_metadata = [LogGroupMetadata.model_validate(lg) for lg in log_groups]
            
            # Get saved queries
            saved_queries = []
            next_token = None

            # No paginator for this API
            while True:
                # TODO: Support other query language types
                kwargs = {'nextToken': next_token, 'queryLanguage': 'CWLI'}
                response = self.logs_client.describe_query_definitions(**remove_null_values(kwargs))
                saved_queries.extend(response.get('queryDefinitions', []))

                next_token = response.get('nextToken')
                if not next_token:
                    break

            logger.info(f'Found {len(saved_queries)} saved queries')
            modeled_queries = [SavedQuery.model_validate(saved_query) for saved_query in saved_queries]

            log_group_targets = {lg.logGroupName for lg in log_group_metadata}
            # filter to only saved queries applicable to log groups we're looking at
            filtered_queries = [
                query
                for query in modeled_queries
                if (query.logGroupNames & log_group_targets)
                or filter_by_prefixes(log_group_targets, query.logGroupPrefixes)
            ]

            return LogMetadata(log_group_metadata=log_group_metadata, saved_queries=filtered_queries)

        except ClientError as e:
            logger.error(f"ClientError in describe_log_groups: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in describe_log_groups: {e}")
            raise
    
    async def analyze_log_group(
        self,
        log_group_arn: str,
        start_time: str,
        end_time: str,
    ) -> LogAnalysisResult:
        """Analyzes a CloudWatch log group for anomalies and patterns."""
        try:
            def is_applicable_anomaly(anomaly: LogAnomaly) -> bool:
                # Must have overlap
                if anomaly.firstSeen > end_time or anomaly.lastSeen < start_time:
                    return False
                # Must be for this log group
                return log_group_arn in anomaly.logGroupArnList

            async def get_applicable_anomalies() -> LogAnomalyResults:
                detectors: List[AnomalyDetector] = []
                paginator = self.logs_client.get_paginator('list_log_anomaly_detectors')
                for page in paginator.paginate(filterLogGroupArn=log_group_arn):
                    detectors.extend(
                        [AnomalyDetector.model_validate(d) for d in page.get('anomalyDetectors', [])]
                    )

                logger.info(f'Found {len(detectors)} anomaly detectors for log group')

                # Get and filter anomalies for each detector
                anomalies: List[LogAnomaly] = []
                for detector in detectors:
                    paginator = self.logs_client.get_paginator('list_anomalies')

                    for page in paginator.paginate(
                        anomalyDetectorArn=detector.anomalyDetectorArn, suppressionState='UNSUPPRESSED'
                    ):
                        anomalies.extend(
                            LogAnomaly.model_validate(anomaly) for anomaly in page.get('anomalies', [])
                        )

                applicable_anomalies = [anomaly for anomaly in anomalies if is_applicable_anomaly(anomaly)]
                logger.info(
                    f'Found {len(anomalies)} anomaly detectors for log group, {len(applicable_anomalies)} of which are applicable'
                )

                return LogAnomalyResults(anomaly_detectors=detectors, anomalies=applicable_anomalies)

            # Run queries in parallel
            log_anomaly_results, pattern_query_result, error_pattern_result = await asyncio.gather(
                get_applicable_anomalies(),
                self.execute_log_insights_query(
                    log_group_identifiers=[log_group_arn],
                    start_time=start_time,
                    end_time=end_time,
                    query_string='pattern @message | sort @sampleCount desc | limit 5',
                    limit=5,
                    max_timeout=30,
                ),
                self.execute_log_insights_query(
                    log_group_identifiers=[log_group_arn],
                    start_time=start_time,
                    end_time=end_time,
                    query_string='fields @timestamp, @message | filter @message like /(?i)(error|exception|fail|timeout|fatal)/ | pattern @message | limit 5',
                    limit=5,
                    max_timeout=30,
                ),
            )

            clean_up_pattern(pattern_query_result.get('results', []))
            clean_up_pattern(error_pattern_result.get('results', []))

            return LogAnalysisResult(
                log_anomaly_results=log_anomaly_results,
                top_patterns=pattern_query_result,
                top_patterns_containing_errors=error_pattern_result,
            )

        except ClientError as e:
            logger.error(f"ClientError in analyze_log_group: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in analyze_log_group: {e}")
            raise
    
    async def execute_log_insights_query(
        self,
        log_group_names: Optional[List[str]] = None,
        log_group_identifiers: Optional[List[str]] = None,
        start_time: str = None,
        end_time: str = None,
        query_string: str = None,
        limit: Optional[int] = None,
        max_timeout: int = 30,
    ) -> Dict:
        """Executes a CloudWatch Logs Insights query and waits for the results."""
        try:
            # Start query
            kwargs = {
                'startTime': int(datetime.datetime.fromisoformat(start_time).timestamp()),
                'endTime': int(datetime.datetime.fromisoformat(end_time).timestamp()),
                'queryString': query_string,
                'logGroupIdentifiers': log_group_identifiers,
                'logGroupNames': log_group_names,
                'limit': limit,
            }

            # Validate that exactly one of log_group_names or log_group_identifiers is provided
            if bool(log_group_names) == bool(log_group_identifiers):
                raise ValueError('Exactly one of log_group_names or log_group_identifiers must be provided')

            start_response = self.logs_client.start_query(**remove_null_values(kwargs))
            query_id = start_response['queryId']
            logger.info(f'Started query with ID: {query_id}')

            # Poll for results
            poll_start = timer()
            while poll_start + max_timeout > timer():
                response = self.logs_client.get_query_results(queryId=query_id)
                status = response['status']

                if status in {'Complete', 'Failed', 'Cancelled'}:
                    logger.info(f'Query {query_id} finished with status {status}')
                    return {
                        'queryId': query_id,
                        'status': status,
                        'statistics': response.get('statistics', {}),
                        'results': [
                            {field['field']: field['value'] for field in line}
                            for line in response.get('results', [])
                        ],
                    }

                await asyncio.sleep(1)

            msg = f'Query {query_id} did not complete within {max_timeout} seconds. Use get_query_results with the returned queryId to try again to retrieve query results.'
            logger.warning(msg)
            return {
                'queryId': query_id,
                'status': 'Polling Timeout',
                'message': msg,
            }

        except ClientError as e:
            logger.error(f"ClientError in execute_log_insights_query: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in execute_log_insights_query: {e}")
            raise
    
    async def get_query_results(
        self,
        query_id: str,
    ) -> Dict:
        """Retrieves the results of a previously started CloudWatch Logs Insights query."""
        try:
            response = self.logs_client.get_query_results(queryId=query_id)

            logger.info(f'Retrieved results for query ID {query_id}')

            return {
                'queryId': query_id,
                'status': response['status'],
                'statistics': response.get('statistics', {}),
                'results': [
                    {field['field']: field['value'] for field in line}
                    for line in response.get('results', [])
                ],
            }
        except ClientError as e:
            logger.error(f"ClientError in get_query_results: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in get_query_results: {e}")
            raise
    
    async def cancel_query(
        self,
        query_id: str,
    ) -> CancelQueryResult:
        """Cancels an ongoing CloudWatch Logs Insights query."""
        try:
            response = self.logs_client.stop_query(queryId=query_id)
            return CancelQueryResult.model_validate(response)
        except ClientError as e:
            logger.error(f"ClientError in cancel_query: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in cancel_query: {e}")
            raise