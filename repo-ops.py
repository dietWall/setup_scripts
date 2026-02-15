#! /usr/bin/env python3

import argparse
from repo_helpers.Repo_Helper import Repo_Helper as docktools
import os.path

helper = docktools()

packages = \
{
    'repo_helper' :{
        "test" : "pytest -s -v tests/test_helper.py",
        "build" : "python -m build ."
    }, 
    'ssh-keys' :{
        "build" : "python -m build .",
        "test" : "pytest -s -v tests/test_ssh_keys.py"
        
    } 
}

def main():
    """Main function to build Docker images and run containers"""
    
    parser = argparse.ArgumentParser(description="Builds and run different images and containers in this repo")
    ops = ["build", "test"]

    parser.add_argument("--package", "-p", help="selects a package", choices=packages, default=None, required=True)
    parser.add_argument("--operations", "-o", help="selects the operations", choices=ops, nargs="+")

    parser.add_argument("--keep_running", 
                        help="keeps the container running for debugging, if any started", 
                        action="store_true", 
                        default=False)

    args = parser.parse_args()
    helper = docktools(None)
    #todo: operations must be: build package, test package, release package,
    #  not build container, run container
    for op in args.operations:
        if op == "build":
            result, output = helper.execute(command=packages[args.package]["build"])
            if result.returncode != 0:
                print(f"build of {args.package} failed with {result.returncode}")
                for l in output:
                    print(l.strip())
            else:
                print(f"build successful")
                for l in output:
                    print(l.strip())
        elif op == "test":
            requirements_file = os.path.join(packages[args.package]["mount_dir"], packages[args.package]["relative_dir"], "requirements.txt")
            print(requirements_file)
            venv_dir=f".venv_{args.package}"
            helper.create_venv_in_container(container_name=args.package, venv_dir=venv_dir)
            helper.exec_in_container_venv(command=f"pip install -r {requirements_file}", container_name=args.package, venv_path=venv_dir)
            helper.exec_in_container_venv(command=packages[args.package]["testcommand"], container_name=args.package, venv_path=venv_dir)

    if args.keep_running == False:
        if helper.get_containers(args.package) != []:
            helper.stop_container(args.package)
            helper.remove_container(args.package)
    else:
        print(f"keeping the container {args.package} running, you can enter it with:")
        print(f"docker exec -it {args.package} bash")

if __name__ == "__main__":
    main()