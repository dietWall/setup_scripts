# setup_scripts
contains some of my scripts to start development faster.  
Since my build and development environment is getting bigger, I wanted to have some reproducible scripts for setting up SSH connections, setting up build environments, docker images, installing software and so on.  
In future, I plan to extend this repo with some additional, reusable functions on demand, so I don´t have to remind how to do this repeating tasks.

# ssh-keys.py
Generates SSH keys on a client PC and (planed!) deploys them to the build/server PC.
Usage:
Run the script on your client PC with --generate [KEY_TYPE] => this generates a new SSH Key  
Run the script on your client PC with --deploy-to-host [USER@HOST] => this should deploy your new SSH Key to the build PC/server. Password will be queried during the process.  
Alternatively you could provide a .env file at repo root with 
```bash
--password_type dotenv --dotenv-file filename 
```
This file requires just one line containing PASSWORD=yourpassword. 

--key-path should provide additional possibilities for operations: generation/deployment. This defaults to .ssh/ directory.  

ssh-keygen is used for generation. This executable is available on all my Linux and Windows environments. For deployment, paramiko is used. 

# Testing

Tests are implemented in tests/ directory.

To install development dependencies (`pytest`, `python-dotenv` etc.):
```bash
pip install -e ".[dev]"
```

To run tests:
```bash
pytest
```

Or with coverage reporting:
```bash
pytest --cov=scripts --cov-report=term-missing
```

To build the package:
```bash
pip install build
python -m build
```


# Improvements / Nice to have
  
If you have any suggestions to improve code/tests, feel free to create a PR for the scripts or write me a message.
More specifically:
- I want to test password prompt automatically.
- add a connection check at the end of test_ssh_keys_deployment
- Remove Password build_arg from dockerfile

