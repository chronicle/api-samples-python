# Chronicle API Samples in Python

Python samples and guidelines for using Chronicle APIs.

## Setup

Follow these instructions: https://cloud.google.com/python/setup

You may skip installing the Cloud Client Libraries and the Cloud SDK, they are
unnecessary for interacting with Chronicle.

After creating and activating a virtual environment, install Python
library dependencies by running this command:

```shell
pip install -r requirements.txt
```

It is assumed that you're using Python 3.7 or above. If you're using an older
Python 3 version, you need to install this backported library as well:

```shell
pip install dataclasses
```

## Credentials

Running the samples requires a JSON credentials file. By default, all the
samples try to use the file `.chronicle_credentials.json` in the user's home
directory. If this file is not found, you need to specify it explicitly by
adding the following argument to the sample's command-line:

`shell -c <file_path>` or `shell --credentials_file <file_path>`

## Usage

You can run samples on the command-line, assuming the current working directory
is the root directory of this repository (i.e. the directory which contains
this `README.md` file):

### Detect API

```shell
python3 -m detect.v2.<sample_name> -h
```

### Lists API

```shell
python3 -m lists.<sample_name> -h
```

### Lists API v1alpha

```shell
python -m lists.v1alpha.create_list -h
python -m lists.v1alpha.get_list -h
python -m lists.v1alpha.patch_list -h
```

## Installing the Chronicle REST API CLI

Install the CLI from source
```
python setup.py install
```

Alternatively, install the CLI from source using make
```
make install
```

Build the wheel file
```
make dist
```

## Using the Chronicle REST API CLI

The CLI provides a unified command-line interface for Chronicle APIs.
The CLI follows this pattern:
```
chronicle [common options] COMMAND_GROUP COMMAND [command options]
```

### Common Options

Common options can be provided either via command-line arguments or environment
variables:

| CLI Option         | Environment Variable        | Description                   |
|--------------------|----------------------------|--------------------------------|
| --credentials-file | CHRONICLE_CREDENTIALS_FILE | Path to service account file   |
| --project-id       | CHRONICLE_PROJECT_ID       | GCP project id or number       |
| --project-instance | CHRONICLE_INSTANCE         | Chronicle instance ID (uuid)   |
| --region           | CHRONICLE_REGION           | Region where project is located|

You can set these options in a `.env` file in your project root:

```bash
# .env file
CHRONICLE_CREDENTIALS_FILE=path/to/credentials.json
CHRONICLE_PROJECT_ID=your-project-id
CHRONICLE_INSTANCE=your-instance-id
CHRONICLE_REGION=your-region
```

The CLI will use values from the `.env` file or a file provided with the
`--env-file` parameter. Command-line options take precedence over environment
variables.

### Command Groups

#### Detection API
```bash
chronicle detect <command-group> <command> [options]
```

Available command groups:

- `alerts`
  - `get <alert-id>`: Get alert by ID
  - `update <alert-id>`: Update an alert
  - `bulk-update`: Bulk update alerts matching a filter

- `detections`
  - `get <detection-id>`: Get detection by ID
  - `list [--filter <filter>]`: List detections

- `rules`
  - `create`: Create a new rule
  - `get <rule-id>`: Get rule by ID
  - `delete <rule-id>`: Delete a rule
  - `enable <rule-id>`: Enable a rule
  - `list [--filter <filter>]`: List rules

- `retrohunts`
  - `create`: Create a new retrohunt
  - `get <retrohunt-id>`: Get retrohunt by ID

- `errors`
  - `list [--filter <filter>]`: List errors

- `rulesets`
  - `batch-update`: Batch update rule set deployments

#### Ingestion API
```bash
chronicle ingestion <command> [options]
```

Available commands:

- `import-events`: Import events into Chronicle
- `get-event <event-id>`: Get event details
- `batch-get-events`: Batch retrieve events

#### Search API
```bash
chronicle search <command> [options]
```

Available commands:

- `find-asset-events [--filter <filter>]`: Find events for an asset
- `find-raw-logs [--filter <filter>]`: Search raw logs
- `find-udm-events [--filter <filter>]`: Find UDM events

#### Lists API
```bash
chronicle lists <command> [options]
```

Available commands:

- `create <name> [--description <desc>] --lines <json-array>`: Create a new list
- `get <list-id>`: Get list by ID
- `patch <list-id> [--description <desc>]
  [--lines-to-add <json-array>] \
  [--lines-to-remove <json-array>]`: Update an existing list

### Examples

Using environment variables (after setting up .env):
```bash
# Get an alert
chronicle detect alerts get --alert-id ABC123 --env-file=.env

# Create a list
chronicle lists create --name "blocklist" --description "Blocked IPs" \
 --lines '["1.1.1.1", "2.2.2.2"]' \
 --env-file=.env

# Search for events
chronicle search find-raw-logs --filter "timestamp.seconds > 1600000000" \
 --env-file=.env

# Override a specific environment variable
chronicle --region us-central1 detect alerts get --alert-id ABC123 \
 --env-file=.env
```

## Running Individual Scripts

You can also run individual API sample scripts directly.
Each script supports the `-h` flag to show available options:

```bash
# Get help for a specific script
python -m detect.v1alpha.get_alert -h
python -m search.v1alpha.find_asset_events -h
python -m lists.v1alpha.patch_list -h
```

## License

Apache 2.0 - See [LICENSE](LICENSE) for more information.
