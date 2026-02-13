#! /usr/bin/env python3


import subprocess
import os

from dataclasses import dataclass

@dataclass
class Container:
    def __init__(self, ps_line:str):
        import re
        str = ps_line.strip()
        str = re.split(r"\s\s\s+", str)
        #index reflects docker ps output
        self.id         = str[0]
        self.image      = str[1]
        self.command    = str[2]
        self.created    = str[3]
        self.status     = str[4]
        #special treatmend if ports exposed
        if len(str) == 7:
            self.ports = str[5]
            self.names = str[6]
        if len(str) == 6:
            self.names = str[5]

    id:         str
    image:      str
    command:    str
    created:    str
    status:     str
    ports:      str|None = None
    names:      str|None = None

class Repo_Helper:
    def __init__(self, logfile: str|None = None) -> None:
        self.logfile = logfile

    def execute(self, command: str, log: bool = False):
        p = subprocess.Popen(executable="/usr/bin/bash", args=command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, shell=True, text=True)
        output = []
        #workaround for Pylance: p.stdout is None, if stdout is not PIPE
        #Pylance complains about it, as we have pipe set, we don´t care
        assert p.stdout is not None 
        
        if self.logfile != None:
            filedesc = open(self.logfile, "a+")
        else: 
            filedesc = None

        for line in p.stdout:  
            output.append(line)
            if log == True:
                print(line, end="")
            if filedesc != None:
                filedesc.write(line)
        p.wait()
        return p, output

    def repo_root(self) -> str:
        command = "git rev-parse --show-toplevel"
        _, output = self.execute(command, False)
        return output[0].strip()

    def build_docker_image(self, dockerfile: str, image_name: str):
        #we need some preparations for relative paths:
        cwd = os.getcwd()
        path = os.path.join(cwd, dockerfile)

        command = f"docker build -t {image_name} {path}"
        result,_ = self.execute(command=command, log=True)
        if result.returncode != 0:
            print(f"docker build failed with: {result}")
            print(f"command was: {command}")
        else:
            print(f"successfully built {image_name} from: {dockerfile}")
        return result

    def start_container(self, image_name: str, container_name: str, mount_dir: str = "/workspace") -> int:
        command = f"docker run --detach -i --name {container_name} --mount type=bind,src={self.repo_root()},dst={mount_dir} {image_name}"
        print(f"starting container from image: {image_name}")
        result, _ = self.execute(command=command)
        if result.returncode != 0:
            print(f"docker run failed with: {result.returncode}")
            print(f"command was: {command}")
        else:
            print(f"successfully started container {container_name} from: {image_name}")
        return result.returncode

    def exec_in_container(self, command: str, container_name: str):
        docker_command = f'docker exec -i {container_name} /bin/bash -c "{command}"'
        result, _ = self.execute(docker_command, log=True)
        if result.returncode != 0:
            print(f"command failed with: {result.returncode}")
            print(f"command was: {command}")
        else:
            print(f"result of: {command} from: {result.returncode}")
        return result.returncode

    def create_venv_in_container(self, container_name: str, venv_dir: str|None = None):
        if venv_dir != None:
            self.exec_in_container(command=f"python3 -m venv {venv_dir}", container_name=container_name)
        else:
            self.exec_in_container(command=f"python3 -m venv .venv", container_name=container_name)

    def exec_in_container_venv(self, command: str, container_name: str, venv_path: str = ".venv_container"):
        docker_command = f'docker exec -i {container_name} /bin/bash -c "source {venv_path}/bin/activate && {command}"'
        result, _ = self.execute(docker_command, log=True)
        if result.returncode != 0:
            print(f"command failed with: {result.returncode}")
            print(f"command was: {command}")
        else:
            print(f"result of: {docker_command} from: {result.returncode}")
        return result

    def compose_up(self, compose_file: str):
        command = f"docker compose -f {compose_file} up -d"
        result, output = self.execute(command)
        
        if result.returncode != 0:
            print(f"command failed with: {result.returncode}")
            print(f"command was: {command}")
        else:
            print(f"result of: {command} from: {result.returncode}")
        return result

    def stop_container(self, container_name: str):
        command = f"docker stop {container_name}"
        result,_ = self.execute(command=command, log=True)
        if result.returncode != 0:
            print(f"docker stop failed with: {result}")
            print(f"command was: {command}")
        else:
            print(f"successfully stopped container {container_name}")
        return result

    def remove_container(self, container_name: str):
        command = f"docker rm {container_name}"
        result, output = self.execute(command=command, log=True)
        if result.returncode != 0:
            print(f"docker rm failed with: {result.returncode}")
            print(f"command was: {command}")
            print(f"output: {output}")
        else:
            print(f"successfully removed container {container_name}")
        return result

    def get_containers(self, image: str|None) -> list[Container]:
        if image != None:
            command = f'docker ps -f "ancestor={image}"'
        else:
            command = f'docker ps -a'
        result, to_strip = self.execute(command)
        output = []
        if result.returncode != 0:
            print(f"docker ps failed with: {result.returncode}")
            print(f"command was: {command}")
            print(f"output: {to_strip}")
        else:
            #prepare output:
            for l in to_strip[1:]: 
                c= Container(l.strip())
                output.append(c)
        return output
    
    def prune(self, force=False):
        if force == False:
            self.execute("docker image prune")
        else:
            self.execute("docker image prune -f")
    
def main():
    import argparse
    import os
    parser = argparse.ArgumentParser(description="Builds and run different images and containers in this repo")

    parser.add_argument("--build",'-b', 
        help="Builds the Docker image, argument is a path to the Dockerfile and an image name", 
        default=None,
        nargs=2, metavar=("Dockerfile", "image_tag")
        )

    parser.add_argument("--run", '-r', 
        help="Runs a container, argument is a docker image tag",
        default=None,
        nargs=2, metavar=("image_tag", "container_name")
        )

    parser.add_argument("--stop", '-s', 
        help="stops a container",
        default=None,
        metavar=("image_tag")
        )
    
    parser.add_argument("--logfile", "-lf", 
        help="writes the build/run logs additionally to a file",
        default=None,
        metavar=("<FILENAME>")
        )
    
    args = parser.parse_args()

    if args.logfile != None:
        helper = Repo_Helper(args.logfile)
    else:
        helper = Repo_Helper(None)

    if args.build != None:
        if os.path.isfile(args.build[0]) == False:
            print(f"Error: {args.build[0]} is not a file")
            return
        print(f"building image: {args.build[1]} from {args.build[0]}")
        helper.build_docker_image(args.build[0], args.build[1])

    if args.run != None:
        helper.start_container(args.run[0], args.run[1])
    
    if args.stop != None:
        helper.stop_container(args.stop[0])

if __name__ == "__main__":
    main()