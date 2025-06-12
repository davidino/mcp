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

"""CloudWatch Logs API routes."""

from typing import Dict, List, Literal, Optional, Any
from mcp.server.fastmcp import Context
from pydantic import Field

from awslabs.cloudwatch_mcp_server.services.logs_service import LogsService
from awslabs.cloudwatch_mcp_server.services.client_factory import ClientFactory
from awslabs.cloudwatch_mcp_server.models.logs_models import LogMetadata, LogAnalysisResult, CancelQueryResult


# Initialize services
logs_client = ClientFactory.get_logs_client()
logs_service = LogsService(logs_client)


async def describe_log_groups_route(
    ctx: Context,
    mcp,
    account_identifiers: Optional[List[str]] = Field(
        None,
        description=(
            'When include_linked_accounts is set to True, use this parameter to specify the list of accounts to search. IMPORTANT: Only has affect if include_linked_accounts is True'
        ),
    ),
    include_linked_accounts: Optional[bool] = Field(
        False,
        description=(
            """If the AWS account is a monitoring account, set this to True to have the tool return log groups in the accounts listed in account_identifiers.
            If this parameter is set to true and account_identifiers contains a null value, the tool returns all log groups in the monitoring account and all log groups in all source accounts that are linked to the monitoring account."""
        ),
    ),
    log_group_class: Optional[Literal['STANDARD', 'INFREQUENT_ACCESS']] = Field(
        None,
        description=('If specified, filters for only log groups of the specified class.'),
    ),
    log_group_name_prefix: Optional[str] = Field(
        None,
        description=(
            'An exact prefix to filter log groups by name. IMPORTANT: Only log groups with names starting with this prefix will be returned.'
        ),
    ),
    max_items: Optional[int] = Field(
        None,
        description=('The maximum number of log groups to return.'),
    ),
) -> LogMetadata:
    """Lists AWS CloudWatch log groups and saved queries associated with them, optionally filtering by a name prefix.

    This tool retrieves information about log groups in the account, or log groups in accounts linked to this account as a monitoring account.
    If a prefix is provided, only log groups with names starting with the specified prefix are returned.

    Additionally returns any user saved queries that are associated with any of the returned log groups.

    Usage: Use this tool to discover log groups that you'd retrieve or query logs from and queries that have been saved by the user.

    Returns:
    --------
    List of log group metadata dictionaries and saved queries associated with them
       Each log group metadata contains details such as:
            - logGroupName: The name of the log group.
            - creationTime: Timestamp when the log group was created
            - retentionInDays: Retention period, if set
            - storedBytes: The number of bytes stored.
            - kmsKeyId: KMS Key Id used for data encryption, if set
            - dataProtectionStatus: Displays whether this log group has a protection policy, or whether it had one in the past, if set
            - logGroupClass: Type of log group class
            - logGroupArn: The Amazon Resource Name (ARN) of the log group. This version of the ARN doesn't include a trailing :* after the log group name.
        Any saved queries that are applicable to the returned log groups are also included.
    """
    try:
        return await logs_service.describe_log_groups(
            account_identifiers=account_identifiers,
            include_linked_accounts=include_linked_accounts,
            log_group_class=log_group_class,
            log_group_name_prefix=log_group_name_prefix,
            max_items=max_items,
        )
    except Exception as e:
        await ctx.error(f'Error in describing log groups: {str(e)}')
        raise


async def analyze_log_group_route(
    ctx: Context,
    mcp,
    log_group_arn: str = Field(
        ...,
        description='The log group arn to look for anomalies in, as returned by the describe_log_groups tools',
    ),
    start_time: str = Field(
        ...,
        description=(
            'ISO 8601 formatted start time for the CloudWatch Logs Insights query window (e.g., "2025-04-19T20:00:00+00:00").'
        ),
    ),
    end_time: str = Field(
        ...,
        description=(
            'ISO 8601 formatted end time for the CloudWatch Logs Insights query window (e.g., "2025-04-19T21:00:00+00:00").'
        ),
    ),
) -> LogAnalysisResult:
    """Analyzes a CloudWatch log group for anomalies, message patterns, and error patterns within a specified time window.

    This tool performs an analysis of the specified log group by:
    1. Discovering and checking log anomaly detectors associated with the log group
    2. Retrieving anomalies from those detectors that fall within the specified time range
    3. Identifying the top 5 most common message patterns
    4. Finding the top 5 patterns containing error-related terms

    Usage: Use this tool to detect anomalies and understand common patterns in your log data, particularly
    focusing on error patterns that might indicate issues. This can help identify potential problems and
    understand the typical behavior of your application.

    Returns:
    --------
    A LogAnalysisResult object containing:
        - log_anomaly_results: Information about anomaly detectors and their findings
            * anomaly_detectors: List of anomaly detectors for the log group
            * anomalies: List of anomalies that fall within the specified time range
        - top_patterns: Results of the query for most common message patterns
        - top_patterns_containing_errors: Results of the query for patterns containing error-related terms
            (error, exception, fail, timeout, fatal)
    """
    try:
        return await logs_service.analyze_log_group(
            log_group_arn=log_group_arn,
            start_time=start_time,
            end_time=end_time,
        )
    except Exception as e:
        await ctx.error(f'Error analyzing log group: {str(e)}')
        raise


async def execute_log_insights_query_route(
    ctx: Context,
    mcp,
    log_group_names: Optional[List[str]] = Field(
        None,
        max_length=50,
        description='The list of up to 50 log group names to be queried. CRITICAL: Exactly one of [log_group_names, log_group_identifiers] should be non-null.',
    ),
    log_group_identifiers: Optional[List[str]] = Field(
        None,
        max_length=50,
        description="The list of up to 50 logGroupIdentifiers to query. You can specify them by the log group name or ARN. If a log group that you're querying is in a source account and you're using a monitoring account, you must use the ARN. CRITICAL: Exactly one of [log_group_names, log_group_identifiers] should be non-null.",
    ),
    start_time: str = Field(
        ...,
        description=(
            'ISO 8601 formatted start time for the CloudWatch Logs Insights query window (e.g., "2025-04-19T20:00:00+00:00").'
        ),
    ),
    end_time: str = Field(
        ...,
        description=(
            'ISO 8601 formatted end time for the CloudWatch Logs Insights query window (e.g., "2025-04-19T21:00:00+00:00").'
        ),
    ),
    query_string: str = Field(
        ...,
        description='The query string in the Cloudwatch Log Insights Query Language. See https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/CWL_QuerySyntax.html.',
    ),
    limit: Optional[int] = Field(
        None,
        description='The maximum number of log events to return. It is critical to use either this parameter or a `| limit <int>` operator in the query to avoid consuming too many tokens of the agent.',
    ),
    max_timeout: int = Field(
        30,
        description='Maximum time in second to poll for complete results before giving up',
    ),
) -> Dict:
    """Executes a CloudWatch Logs Insights query and waits for the results to be available.

    IMPORTANT: The operation must include exactly one of the following parameters: log_group_names, or log_group_identifiers.

    CRITICAL: The volume of returned logs can easily overwhelm the agent context window. Always include a limit in the query
    (| limit 50) or using the limit parameter.

    Usage: Use to query, filter, collect statistics, or find patterns in one or more log groups. For example, the following
    query lists exceptions per hour.

    ```
    filter @message like /Exception/
    | stats count(*) as exceptionCount by bin(1h)
    | sort exceptionCount desc
    ```

    Returns:
    --------
        A dictionary containing the final query results, including:
            - status: The current status of the query (e.g., Scheduled, Running, Complete, Failed, etc.)
            - results: A list of the actual query results if the status is Complete.
            - statistics: Query performance statistics
            - messages: Any informational messages about the query
    """
    try:
        if bool(log_group_names) == bool(log_group_identifiers):
            await ctx.error('Exactly one of log_group_names or log_group_identifiers must be provided')
            raise ValueError('Exactly one of log_group_names or log_group_identifiers must be provided')
            
        return await logs_service.execute_log_insights_query(
            log_group_names=log_group_names,
            log_group_identifiers=log_group_identifiers,
            start_time=start_time,
            end_time=end_time,
            query_string=query_string,
            limit=limit,
            max_timeout=max_timeout,
        )
    except Exception as e:
        await ctx.error(f'Error executing CloudWatch Logs Insights query: {str(e)}')
        raise


async def get_query_results_route(
    ctx: Context,
    mcp,
    query_id: str = Field(
        ...,
        description='The unique ID of the query to retrieve the results for. CRITICAL: This ID is returned by the execute_log_insights_query tool.',
    ),
) -> Dict:
    """Retrieves the results of a previously started CloudWatch Logs Insights query.

    Usage: If a log query is started by execute_log_insights_query tool and has a polling time out, this tool can be used to try to retrieve
    the query results again.

    Returns:
    --------
        A dictionary containing the final query results, including:
            - status: The current status of the query (e.g., Scheduled, Running, Complete, Failed, etc.)
            - results: A list of the actual query results if the status is Complete.
            - statistics: Query performance statistics
            - messages: Any informational messages about the query
    """
    try:
        return await logs_service.get_query_results(query_id=query_id)
    except Exception as e:
        await ctx.error(f'Error retrieving CloudWatch Logs Insights query results: {str(e)}')
        raise


async def cancel_query_route(
    ctx: Context,
    mcp,
    query_id: str = Field(
        ...,
        description='The unique ID of the ongoing query to cancel. CRITICAL: This ID is returned by the execute_log_insights_query tool.',
    ),
) -> CancelQueryResult:
    """Cancels an ongoing CloudWatch Logs Insights query. If the query has already ended, returns an error that the given query is not running.

    Usage: If a log query is started by execute_log_insights_query tool and has a polling time out, this tool can be used to cancel
    it prematurely to avoid incurring additional costs.

    Returns:
    --------
        A CancelQueryResult with a "success" key, which is True if the query was successfully cancelled.
    """
    try:
        return await logs_service.cancel_query(query_id=query_id)
    except Exception as e:
        await ctx.error(f'Error cancelling CloudWatch Logs Insights query: {str(e)}')
        raise


def register_routes(mcp_server):
    """Register all logs routes with the MCP server."""
    mcp_server.tool(name='describe_log_groups')(describe_log_groups_route)
    mcp_server.tool(name='analyze_log_group')(analyze_log_group_route)
    mcp_server.tool(name='execute_log_insights_query')(execute_log_insights_query_route)
    mcp_server.tool(name='get_query_results')(get_query_results_route)
    mcp_server.tool(name='cancel_query')(cancel_query_route)