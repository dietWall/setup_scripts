# setup_scripts
contains some of my scripts to start development faster.  
Since my build and development environment is getting bigger, I wanted to have some reproducible scripts for setting up SSH connections, setting up build environments, docker images, installing software and so on.  
In future, I plan to extend this repo with some additional, reusable functions on demand, so I don´t have to remind how to do this repeating tasks.

# ssh-keys.py
Generates SSH keys on a client PC and (planed!) deploys them to the build/server PC.
Usage:
Run the script on your client PC with --generate [KEY_TYPE] => this generates a new SSH Key  
Run the script on your client PC with --deploy-to-host [USER@HOST] => this should deploy your new SSH Key to the build PC/server. Password will be queried during the process. Alternatively you could provide a .env file with --password_type dotenv and --dotenv-file. This file requires just one line containing PASSWORD=pass. 

--key-path should provide additional possibilities for operations: generation/deployment. This defaults to .ssh/ directory.  

ssh-keygen is used for generation. This executable is available on all my Linux and Windows environments. For deployment, paramiko is used. 

# Testing
Tests are implemented in tests/test-ssh-keys.py
There is a test for each KEY_TYPE generation and KEY_TYPE deployment between from one to another container.

Before running the tests you have to build the docker images. Best approach is to run
```
./docker-operations.py --build test_image
```
This creates a docker image locally from scratch.

This script has also some requirements on the environment. You probably want to create a virtual environment and install requirements.txt first.    

If you want to test ssh-keys.py script manually, you can run  
```
./docker-operations.py --run test_image #starts only one container 
./docker-operations.py --run ssh-network #starts 2 interconnected containers with docker compose
```

This will start a container with the script inside, so you can play around without affecting your client PC.

```
./docker-operations.py --stop test_image
```
stops and removes all containers, defined from the provided Dockerfile.

Since the purpose of the scripts is to modify client/server PCs, the images and containers are only used for testing.


# Improvements / Nice to have
There is no real key management yet. The script fails, if there are existing keys. The script should:
- check if any key already exist
- generate a key with: id_KEY_TYPE_1...n.pub
- transfer the right key accordingly
  
If you have any suggestions to improve the code/testing, feel free to create a PR for the scripts or write me a message.
