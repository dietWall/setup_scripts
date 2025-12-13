#! /usr/bin/env python3

import subprocess
import argparse
import docker
from docker.models.containers import Container as Container

test_image_tag = "ssh-image"

def get_repo_root():
    repo_root = subprocess.run(["git", "rev-parse", "--show-toplevel"],capture_output=True)
    return repo_root.stdout.strip().decode('utf-8')

def load_env() -> bool:
    import os
    if os.path.exists('.env'):
        from dotenv import load_dotenv
        return load_dotenv('.env')
    return False

def build_image() -> bool:
    print(f"building {test_image_tag}")
    build_args = None

    if load_env() == False:
        print("No .env file found or could not be loaded, proceeding without it.")
    else:
        import os
        build_args = {"PASSWORD": os.environ['PASSWORD']}

    client = docker.from_env()
    client.images.build(path=".", tag=test_image_tag, buildargs=build_args)
    print(f"Successfully built image: {test_image_tag}")
    return True

def run_container(image_tag: str) -> Container:
    print(f"Running container from image: {image_tag}")
    import docker.types
    mounts=[docker.types.Mount(target="/home/appuser/code/", source=f"{get_repo_root()}", type="bind", read_only=False)]
    client = docker.from_env()
    
    container = client.containers.run(image_tag, detach=True, tty=True, mounts=mounts)
    print(f"Container {container.id} is running.")
    print(f"enter with: ")
    print(f"docker exec -it {container.name} bash")
    return container

def run_network() -> bool:
    print(f"Running ssh-network using docker-compose")
    repo_root = get_repo_root()
    
    import tests.conftest
    tests.conftest.run_network(repo_root=repo_root)
    containers = tests.conftest.network()
    client_container = tests.conftest.client(containers)
    server_container = tests.conftest.server(containers)

    print(f"enter client with:")
    print(f"docker exec -it {client_container.name} bash")
    print(f"enter server with:")
    print(f"docker exec -it {server_container.name} bash")
    return True

def stop_container(test_image_tag):
    print(f"Stopping and removing containers from image: {test_image_tag}")
    client = docker.from_env()
    containers = client.containers.list(all=True, filters={"ancestor": test_image_tag})
    for container in containers:
        print(f"Stopping container {container.id}...")
        container.stop()
        print(f"Removing container {container.id}...")
        container.remove()
    print("All containers stopped and removed.")
    return True

def main():
    """Main function to build Docker images and run containers"""
    available_images = ['test_image', 'ssh-network']
    parser = argparse.ArgumentParser(description="Builds and run different images and containers in this repo")
    parser.add_argument("--build",'-b', help="Builds the Docker image", choices=available_images, default=None, nargs='?')
    parser.add_argument("--run", '-r', help="Runs the Docker container", choices=available_images, default=None, nargs='?')
    parser.add_argument("--stop", '-s', help="stops all containers with given tag", choices=available_images, default=None, nargs='?')
    args = parser.parse_args()
        
    # Build the image
    if args.build is not None:
        if args.build == 'test_image' or args.build == 'ssh-network':
            build_image()
        else:
            print(f"Unknown image to build: {args.build}")

    if args.run is not None:
        if args.run == 'test_image':
            run_container(test_image_tag)
        elif args.run == 'ssh-network':
            run_network()
        else:
            print(f"Unknown image to run: {args.run}")
    
    if args.stop is not None:
        if args.stop == 'test_image':
            stop_container(test_image_tag)

if __name__ == "__main__":
    main()