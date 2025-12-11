# setup_scripts
contains some scripts to start development faster.  
Since my build and development environment is getting bigger, I wanted to have some reproducible scripts for setting up SSH connections, setting up build environments, docker images, installing software and so on.  
In future, I plan to extend this repo with some additional, reusable functions on demand, so I don´t have to remind how to do this repeating tasks.

# ssh-keys.py
Generates SSH keys on a client PC and (planed!) deploys them to the build/server PC.
Usage:
Run the script on your client PC with --generate [KEY_TYPE] => this generates a new SSH Key  
Run the script on your client PC with --deploy [USER@HOST] => this should deploy your new SSH Key to the build PC/server. Password will be queried during the process.  (Not implemented yet)  
--key-path should provide additional possibilities for operations: generation/deployment.  

ssh-keygen is used for generation. This executable is available on all my Linux and Windows environments.
For deployment I plan to use ssh-copyid on Linux and a custom command on Windows (ssh-copyid is not available on my PCs).

Tests are implemented in tests/test-ssh-keys.py
There is a test for each KEY_TYPE generation in a docker container.
Additionally (planned!) there is a test for deployment each key from a client docker container to a server docker container.

Before running the tests you have to build the docker images. Best approach is to run
```
./docker-operations.py --build test_image
```
This creates a docker image locally from scratch. You should be able to run it manually as well with common docker commands.
This script has also some requirements on the environment. You probably want to create a virtual environment and install requirements.txt in it.    

If you want to test ssh-keys.py script manually, you can run  
```
./docker-operations.py --run test_image
```
This will start a container with the script inside, so you can play around with it without affecting your client PC.    

```
./docker-operations.py --stop test_image
```
stops and removes all containers, defined from the provided Dockerfile.

Since the purpose of the scripts is to modify client/server PCs, the images and containers are only used for testing.

