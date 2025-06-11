# AWS Labs cloudwatch-metrics MCP Server

An AWS Labs Model Context Protocol (MCP) server for cloudwatch-metrics

## Instructions

Use this MCP server to interact with CloudWatch Metrics and Dashboards. Supports retrieving metric data, managing dashboards, working with CloudWatch alarms, and configuring anomaly detection. With CloudWatch, you can monitor your AWS resources and applications in real-time, set alarms, create dashboards, and visualize metrics to help you respond to operational issues.

## Features

- Retrieving metric data from CloudWatch using the GetMetricData API
- Managing CloudWatch dashboards (create, retrieve, list, delete)
- Working with anomaly detection models
- Managing resource tags
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

## Installation

Example for Amazon Q Developer CLI (~/.aws/amazonq/mcp.json):

```json
{
  "mcpServers": {
    "awslabs.cloudwatch-metrics-mcp-server": {
      "autoApprove": [],
      "disabled": false,
      "timeout": 60,
      "command": "uvx",
      "args": [
        "awslabs.cloudwatch-metrics-mcp-server@latest",
      ],
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
2. Go to sub-directory 'src/cloudwatch-metrics-mcp-server/'
3. Run 'docker build -t awslabs/cloudwatch-metrics-mcp-server:latest .'

### Add or update your LLM client's config with following:
```json
{
  "mcpServers": {
    "awslabs.cloudwatch-metrics-mcp-server": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "AWS_PROFILE=[your data]",
        "-e", "AWS_REGION=[your data]",
        "awslabs/cloudwatch-metrics-mcp-server:latest"
      ]
    }
  }
}
```

## Contributing

Contributions are welcome! Please see the [CONTRIBUTING.md](../../CONTRIBUTING.md) in the monorepo root for guidelines.