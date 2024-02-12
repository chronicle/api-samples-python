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

```shell
-c <file_path>
```

or

```shell
--credentials_file <file_path>
```

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

```
python -m lists.v1alpha.create_list -h
python -m lists.v1alpha.get_list -h
python -m lists.v1alpha.patch_list -h
```
