#! /usr/bin/env python3

import argparse
from repo_helpers.Repo_Helper import Repo_Helper as docktools
import os.path

helper = docktools()

packages = \
{
    'repo_helper' :{
        "dir" : os.path.join(helper.repo_root(), "repo_helpers"),
        "relative_dir" : "repo_helpers",
        "testcommand" : "pytest -s -v tests/test_helper.py",
        "mount_dir" : "/workspace/"
    }, 
    'ssh-keys' :{
        "dir" : os.path.join(helper.repo_root(), "ssh"),
        "relative_dir" : "ssh",
        "testcommand" : "pytest -s -v tests/test-ssh-keys.py",
        "mount_dir" : "/workspace/"
    } 
}

def main():
    """Main function to build Docker images and run containers"""
    
    parser = argparse.ArgumentParser(description="Builds and run different images and containers in this repo")
    ops = ["build", "run", "test"]


    parser.add_argument("--package", "-p", help="selects a package", choices=packages, default=None, required=True)
    parser.add_argument("--operations", "-o", help="selects the operations", choices=ops, nargs="+")

    parser.add_argument("--keep_running", 
                        help="keeps the container running for debugging, if any started", 
                        action="store_true", 
                        default=False)

    args = parser.parse_args()
    helper = docktools(None)
    
    for op in args.operations:
        if op == "build":
            helper.build_docker_image(dockerfile=packages[args.package]["dir"], image_name=args.package)
        elif op == "run":
            helper.start_container(image_name=args.package, container_name=args.package, mount_dir=packages[args.package]["mount_dir"])
        elif op == "test":
            requirements_file = os.path.join(packages[args.package]["mount_dir"], packages[args.package]["relative_dir"], "requirements.txt")
            print(requirements_file)
            venv_dir=f".venv_{args.package}"
            helper.create_venv_in_container(container_name=args.package, venv_dir=venv_dir)
            helper.exec_in_container_venv(command=f"pip install -r {requirements_file}", container_name=args.package, venv_path=venv_dir)
            helper.exec_in_container_venv(command=packages[args.package]["testcommand"], container_name=args.package, venv_path=venv_dir)

    if args.keep_running == False:
        helper.stop_container(args.package)
        helper.remove_container(args.package)
    else:
        print(f"keeping the container {args.package} running, you can enter it with:")
        print(f"docker exec -it {args.package} bash")

    #if args.run != None:
        #helper.start_container(image_name=) # (dockerfile=packages[args.build]["dir"], image_name=args.build)


if __name__ == "__main__":
    main()