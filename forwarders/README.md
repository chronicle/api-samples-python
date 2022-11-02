# Forwarder Management APIs

Forwarders are used to ingest security telemetry into a Chronicle instance. While typically found in on-premise environments, they can be deployed almost anywhere that a Docker contain can. For more information regarding the installation and hardware requirements, please see [this installation guide](https://cloud.google.com/chronicle/docs/install/forwarder-linux).

## Overview

At a high-level, a Forwarder is composed of one or more Collectors. Each Collector has its own **ingestion mechanism** (e.g. File, Kafka, PCAP, Splunk, Syslog) and ingests data for a specific **log type**. 

Assuming hardware requirements are met, there may be many Collectors on the same Forwarder to ingest data from a variety of mechanisms and log types. For example, a Forwarder with two syslog Collectors listening for PAN_FIREWALL and CISCO_ASA_FIREWALL data on separate ports, respectively.

## Forwarder API Samples

A Forwarder **must** be created first, and one or more Collectors can be created on that Forwarder. Optionally, configuration settings for Metadata and Regex Filters **may** be configured at the Forwarder level and apply to all of a Forwarder's Collectors. These may be optionally overridden at the Collector level, within the Collector's configuration.

Additionally, default settings for Forwarders and Collectors **may** be set depending on the configuration provided.

### Create Forwarder

Creates a new Forwarder on the Chronicle instance using the configuration specified in the request body.

```shell
$ python -m forwarders.create_forwarder -h
usage: create_forwarder.py [-h] [-c CREDENTIALS_FILE] [-r {asia-southeast1,europe,us}]

optional arguments:
  -h, --help            show this help message and exit
  -c CREDENTIALS_FILE, --credentials_file CREDENTIALS_FILE
                        credentials file path (default: '~/.chronicle_credentials.json')
  -r {asia-southeast1,europe,us}, --region {asia-southeast1,europe,us}
                        the region where the customer is located (default: us)
```
**Example**: Creating a forwarder with the minimum required configuration (`display_name`). By default, the **upload_compression** option will be set.
```shell
$ python -m forwarders.create_forwarder
{
  "name": "forwarders/928b3c1e-1430-4511-892d-2202206b4d8c",
  "displayName": "TestForwarder",
  "config": {
    "uploadCompression": true
  },
  "state": "ACTIVE"
}
```

### Get Forwarder

The format of a Forwarder's **name** is `forwarders/{UUID}`.

```shell
$ python -m forwarders.get_forwarder -h
usage: get_forwarder.py [-h] [-c CREDENTIALS_FILE] [-r {asia-southeast1,europe,us}] -n NAME

optional arguments:
  -h, --help            show this help message and exit
  -c CREDENTIALS_FILE, --credentials_file CREDENTIALS_FILE
                        credentials file path (default: '~/.chronicle_credentials.json')
  -r {asia-southeast1,europe,us}, --region {asia-southeast1,europe,us}
                        the region where the customer is located (default: us)
  -n NAME, --name NAME  unique name for the forwarder
```

**Example**: Retrieving the configuration for `forwarders/928b3c1e-1430-4511-892d-2202206b4d8c`. To retrieve the configuration for the Forwarder's corresponding collectors, the `ListCollectors` API must be used (see below).

```shell
$ python -m forwarders.get_forwarder -n forwarders/928b3c1e-1430-4511-892d-2202206b4d8c
{
  "name": "forwarders/928b3c1e-1430-4511-892d-2202206b4d8c",
  "displayName": "TestForwarder",
  "config": {
    "uploadCompression": true
  },
  "state": "ACTIVE"
}
```

### List Forwarders

Retrieves all Forwarders for the Chronicle instance.

```shell
$ python -m forwarders.list_forwarders -h
usage: list_forwarders.py [-h] [-c CREDENTIALS_FILE] [-r {asia-southeast1,europe,us}]

optional arguments:
  -h, --help            show this help message and exit
  -c CREDENTIALS_FILE, --credentials_file CREDENTIALS_FILE
                        credentials file path (default: '~/.chronicle_credentials.json')
  -r {asia-southeast1,europe,us}, --region {asia-southeast1,europe,us}
                        the region where the customer is located (default: us)
```
Example: Retrieving two Forwarders.
```shell
$ python -m forwarders.list_forwarders
{
    "forwarders": [
        {
            "name": "forwarders/86372ddf-3736-42e8-a78e-aee1a6e3517b",
            "displayName": "TestForwarder2",
            "config": {
                "uploadCompression": true,
                "metadata": {
                    "assetNamespace": "FORWARDER",
                    "labels": [
                        {
                            "key": "office",
                            "value": "corporate"
                        },
                        {
                            "key": "building",
                            "value": "001"
                        }
                    ]
                },
                "regexFilters": [
                    {
                        "description": "TestFilter",
                        "regexp": ".*",
                        "behavior": "ALLOW"
                    }
                ],
                "serverSettings": {
                    "gracefulTimeout": 15,
                    "drainTimeout": 10,
                    "httpSettings": {
                        "port": 8080,
                        "host": "0.0.0.0",
                        "readTimeout": 3,
                        "readHeaderTimeout": 3,
                        "writeTimeout": 3,
                        "idleTimeout": 3,
                        "routeSettings": {
                            "availableStatusCode": 204,
                            "readyStatusCode": 204,
                            "unreadyStatusCode": 503
                        }
                    },
                    "state": "ACTIVE"
                }
            },
            "state": "ACTIVE"
        },
        {
            "name": "forwarders/928b3c1e-1430-4511-892d-2202206b4d8c",
            "displayName": "TestForwarder",
            "config": {
                "uploadCompression": true
            },
            "state": "ACTIVE"
        }
    ]
}
```

### Update Forwarder

An update mask **must** be provided as a request parameter, not in the request body, and indicates which Forwarder fields to update. When updating a list, the entire list will be replaced. In order to append an item to a list, the entire new list must be provided.

```shell
$ python -m forwarders.update_forwarder -h
usage: update_forwarder.py [-h] [-c CREDENTIALS_FILE] [-r {asia-southeast1,europe,us}] -n NAME

optional arguments:
  -h, --help            show this help message and exit
  -c CREDENTIALS_FILE, --credentials_file CREDENTIALS_FILE
                        credentials file path (default: '~/.chronicle_credentials.json')
  -r {asia-southeast1,europe,us}, --region {asia-southeast1,europe,us}
                        the region where the customer is located (default: us)
  -n NAME, --name NAME  unique name for the forwarder
```

**Example**: Updating the display name and adding a metadata label to a Forwarder.
```shell
$ python -m forwarders.create_forwarder
{
  "name": "forwarders/fd9ef30f-79f7-4acb-adfc-32650f6b4c83",
  "displayName": "TestForwarder",
  "config": {
    "uploadCompression": true
  },
  "state": "ACTIVE"
}

$ python -m forwarders.update_forwarder -n forwarders/fd9ef30f-79f7-4acb-adfc-32650f6b4c83
{
  "name": "forwarders/fd9ef30f-79f7-4acb-adfc-32650f6b4c83",
  "displayName": "UpdatedForwarder",
  "config": {
    "uploadCompression": true,
    "metadata": {
      "labels": [
        {
          "key": "office",
          "value": "corporate"
        }
      ]
    }
  },
  "state": "ACTIVE"
}
```

### Delete Forwarder

After successfully deleting a Forwarder, the response message is expected to be **empty**.

```shell
$ python -m forwarders.delete_forwarder -h
usage: delete_forwarder.py [-h] [-c CREDENTIALS_FILE] [-r {asia-southeast1,europe,us}] -n NAME

optional arguments:
  -h, --help            show this help message and exit
  -c CREDENTIALS_FILE, --credentials_file CREDENTIALS_FILE
                        credentials file path (default: '~/.chronicle_credentials.json')
  -r {asia-southeast1,europe,us}, --region {asia-southeast1,europe,us}
                        the region where the customer is located (default: us)
  -n NAME, --name NAME  unique name for the forwarder
```
Example: Deleting forwarder with name `forwarders/928b3c1e-1430-4511-892d-2202206b4d8c`.
```shell
$ python -m forwarders.delete_forwarder -n forwarders/928b3c1e-1430-4511-892d-2202206b4d8c
{}
```

## Collector Commands

A Forwarder must exist **before** a Collector can be created.

### Create Collector

```shell
$ python -m forwarders.create_collector -h
usage: create_collector.py [-h] [-c CREDENTIALS_FILE] [-r {asia-southeast1,europe,us}] -f FORWARDER

optional arguments:
  -h, --help            show this help message and exit
  -c CREDENTIALS_FILE, --credentials_file CREDENTIALS_FILE
                        credentials file path (default: '~/.chronicle_credentials.json')
  -r {asia-southeast1,europe,us}, --region {asia-southeast1,europe,us}
                        the region where the customer is located (default: us)
  -f FORWARDER, --forwarder FORWARDER
                        name of the forwarder on which to add the collector
```

**Example**: Creating a syslog Collector which uses TCP to listen on port 10514 on Forwarder (`forwarders/86372ddf-3736-42e8-a78e-aee1a6e3517b`). 

```shell
$ python -m forwarders.create_collector -f forwarders/86372ddf-3736-42e8-a78e-aee1a6e3517b
{
  "name": "forwarders/86372ddf-3736-42e8-a78e-aee1a6e3517b/collectors/5d346ec1-ece1-44c6-94bc-04681e5d9d8a",
  "displayName": "SyslogCollector1",
  "config": {
    "logType": "PAN_FIREWALL",
    "maxSecondsPerBatch": 10,
    "maxBytesPerBatch": "1048576",
    "syslogSettings": {
      "protocol": "TCP",
      "address": "0.0.0.0",
      "port": 10514,
      "bufferSize": "65536",
      "connectionTimeout": 60
    }
  },
  "state": "ACTIVE"
}
```

### Get Collector

The format of a Collector's **name** is `forwarders/{forwarderUUID}/collectors/{collectorUUID}`.

```shell
$ python -m forwarders.get_collector -h
usage: get_collector.py [-h] [-c CREDENTIALS_FILE] [-r {asia-southeast1,europe,us}] -n NAME

optional arguments:
  -h, --help            show this help message and exit
  -c CREDENTIALS_FILE, --credentials_file CREDENTIALS_FILE
                        credentials file path (default: '~/.chronicle_credentials.json')
  -r {asia-southeast1,europe,us}, --region {asia-southeast1,europe,us}
                        the region where the customer is located (default: us)
  -n NAME, --name NAME  unique name for the collector
```

**Example**: Retrieving the configuration for Collector with name `forwarders/86372ddf-3736-42e8-a78e-aee1a6e3517b/collectors/5d346ec1-ece1-44c6-94bc-04681e5d9d8a`.

```shell
$ python -m forwarders.get_collector -n forwarders/86372ddf-3736-42e8-a78e-aee1a6e3517b/collectors/5d346ec1-ece1-44c6-94bc-04681e5d9d8a
{
  "name": "forwarders/86372ddf-3736-42e8-a78e-aee1a6e3517b/collectors/5d346ec1-ece1-44c6-94bc-04681e5d9d8a",
  "displayName": "SyslogCollector1",
  "config": {
    "logType": "PAN_FIREWALL",
    "maxSecondsPerBatch": 10,
    "maxBytesPerBatch": "1048576",
    "syslogSettings": {
      "protocol": "TCP",
      "address": "0.0.0.0",
      "port": 10514,
      "bufferSize": "65536",
      "connectionTimeout": 60
    }
  },
  "state": "ACTIVE"
}
```

### List Collectors

Retrieves all Collectors belonging to the specified Forwarder.

```shell
$ python -m forwarders.list_collectors -h
usage: list_collectors.py [-h] [-c CREDENTIALS_FILE] [-r {asia-southeast1,europe,us}] -f FORWARDER

optional arguments:
  -h, --help            show this help message and exit
  -c CREDENTIALS_FILE, --credentials_file CREDENTIALS_FILE
                        credentials file path (default: '~/.chronicle_credentials.json')
  -r {asia-southeast1,europe,us}, --region {asia-southeast1,europe,us}
                        the region where the customer is located (default: us)
  -f FORWARDER, --forwarder FORWARDER
                        unique name for the forwarder
```

Example: Retrieving all Collectors associated with Forwarder (`forwarders/86372ddf-3736-42e8-a78e-aee1a6e3517b`)

```shell
$ python -m forwarders.list_collectors -f forwarders/86372ddf-3736-42e8-a78e-aee1a6e3517b
{
  "collectors": [
    {
      "name": "forwarders/86372ddf-3736-42e8-a78e-aee1a6e3517b/collectors/52d658fc-2d51-4a8a-8986-425195a28ffb",
      "displayName": "SplunkCollector",
      "config": {
        "logType": "WINDOWS_DNS",
        "maxSecondsPerBatch": 10,
        "maxBytesPerBatch": "1048576",
        "splunkSettings": {
          "host": "127.0.0.1",
          "minimumWindowSize": 10,
          "maximumWindowSize": 30,
          "queryString": "search index=* sourcetype=dns",
          "queryMode": "realtime",
          "port": 8089
        }
      },
      "state": "ACTIVE"
    },
    {
      "name": "forwarders/86372ddf-3736-42e8-a78e-aee1a6e3517b/collectors/5d346ec1-ece1-44c6-94bc-04681e5d9d8a",
      "displayName": "SyslogCollector1",
      "config": {
        "logType": "PAN_FIREWALL",
        "maxSecondsPerBatch": 10,
        "maxBytesPerBatch": "1048576",
        "syslogSettings": {
          "protocol": "TCP",
          "address": "0.0.0.0",
          "port": 10514,
          "bufferSize": "65536",
          "connectionTimeout": 60
        }
      },
      "state": "ACTIVE"
    }
  ]
}
```

### Update Collector

An update mask **must** be provided as a request parameter, not in the request body, and indicates which Collector fields to update. When updating a list, the entire list will be replaced. In order to append an item to a list, the entire new list must be provided.

```shell
$ python -m forwarders.update_collector -h
usage: update_collector.py [-h] [-c CREDENTIALS_FILE] [-r {asia-southeast1,europe,us}] -n NAME

optional arguments:
  -h, --help            show this help message and exit
  -c CREDENTIALS_FILE, --credentials_file CREDENTIALS_FILE
                        credentials file path (default: '~/.chronicle_credentials.json')
  -r {asia-southeast1,europe,us}, --region {asia-southeast1,europe,us}
                        the region where the customer is located (default: us)
```

**Example**: Creating and then updating a file Collector's `display_name`, `log_type`, and `file_path`.

```shell
$ python -m forwarders.create_collector -f forwarders/86372ddf-3736-42e8-a78e-aee1a6e3517b
{
  "name": "forwarders/86372ddf-3736-42e8-a78e-aee1a6e3517b/collectors/f6da4e72-52e1-4a41-8979-17d5cabd78c5",
  "displayName": "FileCollector",
  "config": {
    "logType": "WINDOWS_DNS",
    "maxSecondsPerBatch": 10,
    "maxBytesPerBatch": "1048576",
    "fileSettings": {
      "filePath": "/path/to/log.file"
    }
  },
  "state": "ACTIVE"
}

$ python -m forwarders.update_collector -n forwarders/86372ddf-3736-42e8-a78e-aee1a6e3517b/collectors/f6da4e72-52e1-4a41-8979-17d5cabd78c5
{
  "name": "forwarders/86372ddf-3736-42e8-a78e-aee1a6e3517b/collectors/f6da4e72-52e1-4a41-8979-17d5cabd78c5",
  "displayName": "UpdatedCollector",
  "config": {
    "logType": "WINDOWS_DNS",
    "maxSecondsPerBatch": 10,
    "maxBytesPerBatch": "1048576",
    "fileSettings": {
      "filePath": "/new/path/to/file.txt"
    }
  },
  "state": "ACTIVE"
}
```

### Delete Collector

The format of a Collector's **name** is `forwarders/{forwarderUUID}/collectors/{collectorUUID}`.

```shell
python -m forwarders.delete_collector -h
usage: delete_collector.py [-h] [-c CREDENTIALS_FILE] [-r {asia-southeast1,europe,us}] -n NAME

optional arguments:
  -h, --help            show this help message and exit
  -c CREDENTIALS_FILE, --credentials_file CREDENTIALS_FILE
                        credentials file path (default: '~/.chronicle_credentials.json')
  -r {asia-southeast1,europe,us}, --region {asia-southeast1,europe,us}
                        the region where the customer is located (default: us)
  -n NAME, --name NAME  unique name for the collector
```

**Example**: Deleting a Collector with name `forwarders/86372ddf-3736-42e8-a78e-aee1a6e3517b/collectors/f6da4e72-52e1-4a41-8979-17d5cabd78c5`.

```shell
$ python -m forwarders.delete_collector -n forwarders/86372ddf-3736-42e8-a78e-aee1a6e3517b/collectors/f6da4e72-52e1-4a41-8979-17d5cabd78c5
{}
```

## Generating Configuration Files

To generate a Forwarder's configuration files, at least one Collector **must** exist. By default, this command will print the file contents to the terminal, though the `-o` option may be provided to write the configuration and auth files to `forwarder.conf` and `forwarder_auth.conf`, respectively. These files will need to be transferred to the Forwarder's host and the Forwarder must be restarted for changes to take effect.

Note: The files **must not** be modified. Any changes should be applied using the Update methods above, and then the configuration may be re-generated.

```shell
$ python -m forwarders.generate_files -h
usage: generate_files.py [-h] [-c CREDENTIALS_FILE] [-r {asia-southeast1,europe,us}] -n NAME [-o OUTPUT]

optional arguments:
  -h, --help            show this help message and exit
  -c CREDENTIALS_FILE, --credentials_file CREDENTIALS_FILE
                        credentials file path (default: '~/.chronicle_credentials.json')
  -r {asia-southeast1,europe,us}, --region {asia-southeast1,europe,us}
                        the region where the customer is located (default: us)
  -n NAME, --name NAME  name of the forwarder
  -o OUTPUT, --output OUTPUT
                        Writes configuration files to the specified output directory.
```

**Example**: Printing the file contents to the terminal.

```shell
$ python -m forwarders.generate_files -v -n forwarders/86372ddf-3736-42e8-a78e-aee1a6e3517b
forwarder.conf:
 output:
  compression: true
  url: test-malachiteingestion-pa.sandbox.googleapis.com:443
  identity:
    collector_id: 86372ddf-3736-42e8-a78e-aee1a6e3517b
    customer_id: c2966ae6-d4c3-4c3b-a315-e672b3a0d498
regex_filters:
  TestFilter:
    regexp: .*
    behavior_on_match: allow
metadata:
  labels:
    building: "001"
    office: corporate
  namespace: FORWARDER
collectors:
- splunk:
    common:
      enabled: true
      data_type: WINDOWS_DNS
      batch_n_seconds: 10
      batch_n_bytes: 1048576
    url: 127.0.0.1:8089
    minimum_window_size: 10
    maximum_window_size: 30
    query_string: search index=* sourcetype=dns
    query_mode: realtime
- syslog:
    common:
      enabled: true
      data_type: PAN_FIREWALL
      batch_n_seconds: 10
      batch_n_bytes: 1048576
    tcp_address: 0.0.0.0:10514
    tcp_buffer_size: 65536
    connection_timeout_sec: 60

forwarder_auth.conf:
 output:
  identity:
    secret_key:  <REDACTED>
collectors:
- splunk:
    auth: true
    username: admin
    password: pass
- syslog:
    auth: true
```

**Example**: Writing the configuration files to the `~/Downloads` directory.

```shell
$ python -m forwarders.generate_files -n forwarders/86372ddf-3736-42e8-a78e-aee1a6e3517b -o ~/Downloads

$ ll ~/Downloads
-rw-r--r--  1 user  primarygroup   1.3K Oct 31 15:08 forwarder.conf
-rw-r--r--  1 user  primarygroup   2.5K Oct 31 15:08 forwarder_auth.conf
```