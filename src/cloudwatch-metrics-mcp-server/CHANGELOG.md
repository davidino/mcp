# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.2] - 2025-06-07

### Fixed
- Fixed timestamp conversion in MetricDataResult and MetricStatistics models to properly handle datetime objects
- Improved error handling for different timestamp formats

## [0.0.1] - 2023-06-01

### Added
- Initial release of the CloudWatch Metrics MCP server
- Support for listing metrics with the `list_metrics` tool
- Support for retrieving metric data with the `get_metric_data` tool
- Support for retrieving metric statistics with the `get_metric_statistics` tool
