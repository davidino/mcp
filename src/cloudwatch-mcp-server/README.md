# AWS Labs CloudWatch MCP Server

An AWS Labs Model Context Protocol (MCP) server for CloudWatch

## Instructions

Use this MCP server to interact with CloudWatch. Supports retrieving metric data, managing dashboards, working with CloudWatch alarms, analyzing CloudWatch Logs, and configuring anomaly detection. With CloudWatch, you can monitor your AWS resources and applications in real-time, set alarms, create dashboards, visualize metrics, and analyze logs to help you respond to operational issues.

## Features

- Retrieving metric data from CloudWatch using the GetMetricData API
- Managing CloudWatch dashboards (create, retrieve, list, delete)
- Working with anomaly detection models
- Managing resource tags
- Analyzing CloudWatch Logs with Logs Insights queries
- Detecting anomalies in log groups
- Converting human-readable questions and commands into CloudWatch metric queries

## Prerequisites

1. Install `uv` from [Astral](https://docs.astral.sh/uv/getting-started/installation/) or the [GitHub README](https://github.com/astral-sh/uv#installation)
2. Install Python using `uv python install 3.10`
3. An AWS account with [CloudWatch Metrics](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/working_with_metrics.html)
4. This MCP server can only be run locally on the same host as your LLM client.
5. Set up AWS credentials with access to AWS services
   - You need an AWS account with appropriate permissions
   - Configure AWS credentials with `aws configure` or environment variables

## Available Tools

### Metrics
* `list_metrics` - Lists metrics for the specified namespace, optionally filtered by metric name, dimensions, or tags.
* `get_metric_data` - Retrieves metric data from CloudWatch using metric queries with specified time range and period.
* `get_metric_statistics` - Retrieves statistics for the specified metric, with options for time range, period, and statistics types.
* `put_metric_data` - Publishes metric data points to Amazon CloudWatch.
* `get_metric_widget_image` - Gets a snapshot graph of one or more CloudWatch metrics as a bitmap image.

### Logs
* `describe_log_groups` - Lists AWS CloudWatch log groups and saved queries associated with them.
* `analyze_log_group` - Analyzes a CloudWatch log group for anomalies, message patterns, and error patterns.
* `execute_log_insights_query` - Executes a CloudWatch Logs Insights query and waits for the results.
* `get_query_results` - Retrieves the results of a previously started CloudWatch Logs Insights query.
* `cancel_query` - Cancels an ongoing CloudWatch Logs Insights query.

### Dashboards
* `delete_dashboards` - Deletes one or more CloudWatch dashboards.
* `get_dashboard` - Retrieves the specified CloudWatch dashboard.
* `list_dashboards` - Lists the CloudWatch dashboards in your account.
* `put_dashboard` - Creates or updates a CloudWatch dashboard.

### Alarms
* `delete_alarms` - Deletes the specified CloudWatch alarms.
* `describe_alarm_history` - Retrieves the history for the specified alarm.
* `describe_alarms` - Retrieves information about the specified alarms.
* `desc_alarms_for_metric` - Retrieves all alarms for a specified metric.
* `disable_alarm_actions` - Disables actions for the specified alarms.
* `enable_alarm_actions` - Enables actions for the specified alarms.
* `put_composite_alarm` - Creates or updates a composite alarm.
* `put_metric_alarm` - Creates or updates a metric alarm.
* `set_alarm_state` - Temporarily sets the state of an alarm.

### Anomaly Detection
* `delete_anomaly_detector` - Deletes an anomaly detection model for a CloudWatch metric.
* `desc_anomaly_detectors` - Lists the anomaly detection models that you have created.
* `put_anomaly_detector` - Creates or updates an anomaly detection model for a CloudWatch metric.

### Metric Streams
* `delete_metric_stream` - Deletes the specified metric stream.
* `get_metric_stream` - Retrieves the specified metric stream.
* `list_metric_streams` - Lists the metric streams in your account.
* `put_metric_stream` - Creates or updates a metric stream.
* `start_metric_streams` - Starts the specified metric streams.
* `stop_metric_streams` - Stops the specified metric streams.

### Insight Rules
* `delete_insight_rules` - Deletes the specified Contributor Insights rules.
* `desc_insight_rules` - Returns a list of all Contributor Insights rules in your account.
* `disable_insight_rules` - Disables the specified Contributor Insights rules.
* `enable_insight_rules` - Enables the specified Contributor Insights rules.
* `get_insight_rule_report` - Returns data about the contributors for the specified rule.
* `list_managed_insight_rules` - Returns a list of managed Contributor Insights rules for a specific AWS resource.
* `put_insight_rule` - Creates a Contributor Insights rule.
* `put_managed_insight_rules` - Creates managed Contributor Insights rules for a specified AWS resource.

### Observability Access Manager (OAM)
* `list_oam_sinks` - Lists OAM sinks in your AWS account.
* `get_oam_sink` - Gets details about a specific OAM sink.
* `create_oam_sink` - Creates a new OAM sink in your AWS account.
* `update_oam_sink` - Updates an existing OAM sink.
* `delete_oam_sink` - Deletes an OAM sink from your AWS account.
* `list_oam_links` - Lists OAM links in your AWS account.
* `get_oam_link` - Gets details about a specific OAM link.
* `create_oam_link` - Creates a new OAM link to connect a source account to a monitoring account sink.
* `update_oam_link` - Updates an existing OAM link.
* `delete_oam_link` - Deletes an OAM link from your AWS account.
* `list_attached_oam_links` - Lists links attached to a specific OAM sink.

### Tags
* `list_tags_for_resource` - Lists the tags for a CloudWatch resource.
* `tag_resource` - Adds or modifies tags for a CloudWatch resource.
* `untag_resource` - Removes tags from a CloudWatch resource.

### Required IAM Permissions
* `cloudwatch:ListMetrics`
* `cloudwatch:GetMetricData`
* `cloudwatch:GetMetricStatistics`
* `cloudwatch:PutMetricData`
* `cloudwatch:GetMetricWidgetImage`
* `cloudwatch:DeleteDashboards`
* `cloudwatch:GetDashboard`
* `cloudwatch:ListDashboards`
* `cloudwatch:PutDashboard`
* `cloudwatch:DeleteAlarms`
* `cloudwatch:DescribeAlarmHistory`
* `cloudwatch:DescribeAlarms`
* `cloudwatch:DescribeAlarmsForMetric`
* `cloudwatch:DisableAlarmActions`
* `cloudwatch:EnableAlarmActions`
* `cloudwatch:PutCompositeAlarm`
* `cloudwatch:PutMetricAlarm`
* `cloudwatch:SetAlarmState`
* `cloudwatch:DeleteAnomalyDetector`
* `cloudwatch:DescribeAnomalyDetectors`
* `cloudwatch:PutAnomalyDetector`
* `cloudwatch:ListTagsForResource`
* `cloudwatch:TagResource`
* `cloudwatch:UntagResource`
* `cloudwatch:DeleteInsightRules`
* `cloudwatch:DescribeInsightRules`
* `cloudwatch:DisableInsightRules`
* `cloudwatch:EnableInsightRules`
* `cloudwatch:GetInsightRuleReport`
* `cloudwatch:ListManagedInsightRules`
* `cloudwatch:PutInsightRule`
* `cloudwatch:PutManagedInsightRules`
* `cloudwatch:DeleteMetricStream`
* `cloudwatch:GetMetricStream`
* `cloudwatch:ListMetricStreams`
* `cloudwatch:PutMetricStream`
* `cloudwatch:StartMetricStreams`
* `cloudwatch:StopMetricStreams`
* `logs:DescribeLogGroups`
* `logs:StartQuery`
* `logs:GetQueryResults`
* `logs:StopQuery`
* `logs:DescribeQueryDefinitions`
* `logs:ListLogAnomalyDetectors`
* `logs:ListAnomalies`
* `oam:ListSinks`
* `oam:GetSink`
* `oam:CreateSink`
* `oam:UpdateSink`
* `oam:DeleteSink`
* `oam:ListLinks`
* `oam:GetLink`
* `oam:CreateLink`
* `oam:UpdateLink`
* `oam:DeleteLink`
* `oam:ListAttachedLinks`

## Development

### Running the Server

To run the server locally for development:

```bash
./run.sh
```

This script:
1. Creates a virtual environment if it doesn't exist
2. Installs the package and its dependencies
3. Runs the server

### Running Tests

To run the tests, use the provided script:

```bash
./run-test.sh
```

This script:
1. Creates a test virtual environment if it doesn't exist
2. Installs the package and test dependencies
3. Runs all tests

You can also:
- Run specific test files: `./run-test.sh tests/unit/test_logs_service.py`
- Run tests with verbose output: `./run-test.sh --verbose` or `./run-test.sh -v`

## Installation

Example for Amazon Q Developer CLI (~/.aws/amazonq/mcp.json):

```json
{
  "mcpServers": {
    "awslabs.cloudwatch-mcp-server": {
      "autoApprove": [],
      "disabled": false,
      "timeout": 60,
      "command": "<your-path-to>/mcp/src/cloudwatch-mcp-server/run.sh",
      "args": [],
      "env": {
        "AWS_PROFILE": "[The AWS Profile Name to use for AWS access]",
        "AWS_REGION": "[The AWS region to run in]",
        "FASTMCP_LOG_LEVEL": "ERROR"
      },
      "transportType": "stdio"
    }
  }
}
```

### Build and install docker image locally on the same host of your LLM client

1. `git clone https://github.com/awslabs/mcp.git`
2. Go to sub-directory 'src/cloudwatch-mcp-server/'
3. Run 'docker build -t awslabs/cloudwatch-mcp-server:latest .'

### Add or update your LLM client's config with following:
```json
{
  "mcpServers": {
    "awslabs.cloudwatch-mcp-server": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "AWS_PROFILE=[your data]",
        "-e", "AWS_REGION=[your data]",
        "awslabs/cloudwatch-mcp-server:latest"
      ]
    }
  }
}
```

## Contributing

Contributions are welcome! Please see the [CONTRIBUTING.md](../../CONTRIBUTING.md) in the monorepo root for guidelines.