In this directory and its children, we provide two utilities to use the Rules
Engine API:

*   A library for calling the Rules Engine API, in `rule_lib.py`.
*   A CLI tool, [`cli/rule_cmd.py`](./cli/rule_cmd.py).

You should use a virtual environment, which will manage all the dependencies for
you. To set one up, and install all dependencies:

```
# cd to the root of the Chronicle git repo, which contains requirements.txt
$ python3 -m venv venv              # Create a virtual environment, called venv
$ source venv/bin/activate          # Enter the virtual environment
$ pip3 install -r requirements.txt  # Install all required dependencies
```

You can then run `deactivate` any time to exit the virtual environment. If you
wish to run the scripts again later, you will need to first run `source
venv/bin/activate` again. The CLI tool requires some arguments; look in the
rule_cmd.py file to see these.

As an example, to list your rules:

```
# cd to the cli directory
$ python3 rule_cmd.py ListRules -v
```

Also note that both scripts require a credentials file. Specifically, they will
both look for the file under your home directory, `~/bk_credentials.json`.

If you want to directly use `rule_lib.py`, you will have to install the google
API dependency:

```
$ pip3 install google-api-python-client
```

