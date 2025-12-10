#! /usr/bin/env python3

import subprocess
import argparse

test_image_tag = "ssh-image"

def build_image(ssh_script_path):
    print(f"building {test_image_tag} with ssh script at: {ssh_script_path}")
    import docker
    client = docker.from_env()
    client.images.build(path=".", tag=test_image_tag, buildargs={"SSH_SCRIPT_PATH": ssh_script_path})
    print(f"Successfully built image: {test_image_tag}")
    return True

def run_container(image_tag):
    print(f"Running container from image: {image_tag}")
    import docker
    client = docker.from_env()
    container = client.containers.run(image_tag, detach=True, tty=True)
    print(f"Container {container.id} is running.")
    print(f"enter with: ")
    print(f"docker exec -it {container.name} bash")
    return container

def stop_container(test_image_tag):
    print(f"Stopping and removing containers from image: {test_image_tag}")
    import docker
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
    available_images = ['test_image']
    parser = argparse.ArgumentParser(description="Builds and run different images and containers in this repo")
    parser.add_argument("--build",'-b', help="Builds the Docker image", choices=available_images, default=None, nargs='?')
    parser.add_argument("--run", '-r', help="Runs the Docker container", choices=available_images, default=None, nargs='?')
    parser.add_argument("--stop", '-s', help="stops all containers with given tag", choices=available_images, default=None, nargs='?')
    args = parser.parse_args()
        
    # Build the image
    if args.build is not None:
        if args.build == 'test_image':
            repo_root = subprocess.run(["git", "rev-parse", "--show-toplevel"],capture_output=True)
            build_image(f"{repo_root.stdout.strip().decode('utf-8')}/ssh/ssh-keys.py")

    if args.run is not None:
        if args.run == 'test_image':
            run_container(test_image_tag)
    
    if args.stop is not None:
        if args.stop == 'test_image':
            stop_container(test_image_tag)

if __name__ == "__main__":
    main()