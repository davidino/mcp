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

### CloudWatch Metrics
  * List available metrics in your AWS account
  * Retrieve metric data for analysis and visualization
  * Get statistical data for specific metrics
  * Publish custom metric data to CloudWatch
  * Generate metric visualizations as images

### CloudWatch Logs
  * List and filter log groups
  * Analyze log groups for anomalies and patterns
  * Run CloudWatch Logs Insights queries
  * Manage query results and cancel queries

### CloudWatch Dashboards
  * Create and update dashboards
  * Retrieve dashboard details
  * List dashboards in your account
  * Delete dashboards

### CloudWatch Alarms
  * Retrieve alarm history and information
  * Create and update metric and composite alarms
  * Delete alarms
  * Enable and disable alarm actions
  * Set alarm states

### CloudWatch Anomaly Detection
Tool for working with CloudWatch Anomaly Detectors
  * Create and update anomaly detection models
  * List existing anomaly detectors
  * Delete anomaly detectors

### CloudWatch Metric Streams
  * Create and update metric streams
  * List and retrieve metric stream details
  * Start and stop metric streams
  * Delete metric streams

### CloudWatch Insight Rules
  * Create and manage Contributor Insights rules
  * Retrieve rule reports and data
  * Enable and disable rules
  * Manage managed rules for AWS resources

### CloudWatch Observability Access Manager (OAM)
  * Managing OAM sinks for monitoring accounts
  * Managing OAM links for source accounts
  * Listing and filtering sinks and links
  * Creating cross-account observability configurations

### CloudWatch Tags
  * List tags for CloudWatch resources
  * Add or modify tags for resources
  * Remove tags from resources

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

### Project Structure

The project uses a tool-based architecture:
- `tools/`: Contains all CloudWatch tool implementations organized by functionality
- `models/`: Contains data models used by the tools
- `services/`: Contains service implementations that interact with AWS APIs

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