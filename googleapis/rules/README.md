In this directory and its children, we provide two utilities to use the Rules
Engine API:

*   A library for calling the Rules Engine API, in `rule_lib.py`.
*   A CLI tool, `cli/rule_cmd.py`.

If you want to directly use `rule_lib.py` you will have to install the google
API dependency:

```
pip3 install google-api-client
```

For the two binaries (the CLI and the UI), you should use a virtual environment.
This will manage all the dependencies for you. To set one up (from either the
`cli` or `ui` folder):

```
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

This will create a virtual environment and install all the required
dependencies. You can then run the scripts directly. From the `cli` folder:

```
python3 rule_cmd.py
```

(Note that the CLI tool requires some arguments: you can look in the file to see
these).

You can then run `deactivate` any time to exit the virtual environment. If you
wish to run the scripts again later, you will need to run `source
venv/bin/activate` again.

The last thing to note is that both scripts require a credentials file.
Specifically, they will both look for the file under your home directory,
`~/bk_credentials.json`.
