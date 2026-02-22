
import pytest
import os

from repo_helpers.Repo_Helper import Repo_Helper

@pytest.mark.parametrize("log", ["image_build.txt", None])
def test_build_image(log, log_dir):
    image_name = "repo_helper_test"

    if log != None:
        logfile = os.path.join(log_dir, log)
    else: logfile = None

    docker = Repo_Helper(logfile=logfile)

    docker.prune(True)

    this_dir = os.path.dirname(__file__)
    datadir = os.path.join(this_dir, "data")

    result = docker.build_docker_image(datadir, image_name)
    assert result.returncode == 0, f"Build Image failed with return code: {result.returncode}"

    if logfile != None:
        assert os.path.isfile(logfile), f"Logfile has not been created {result.returncode}"

@pytest.mark.parametrize( "image,container_name", [("ubuntu", "ubuntu_con"), ("debian", "deb_con")] )
def test_run_container(cleanup, image, container_name):
    docker = Repo_Helper(logfile=None)
    result = docker.start_container(image, container_name)
    assert result == 0, f"Error container {container_name} from {image} failed to start with {result}"

@pytest.mark.parametrize("command", ["ls -la", "echo hello world", "docker ps"])
def test_execute_local(command):
    helper = Repo_Helper(logfile=None)
    result, output = helper.execute(command=command, log=False)
    assert(result.returncode == 0), f"Command {command} has failed with exitcode: {result.returncode}"

#this should be tested, if git is not installed => create a container
def test_repo_root():
    this_dir = os.path.dirname(__file__)
    one_dir_up = os.path.join(this_dir, "..")
    repo_root = os.path.abspath(one_dir_up)
    
    helper = Repo_Helper(None)
    helper_repo_root = helper.repo_root()
    assert(repo_root == helper_repo_root), f"Calculated Repo Root = {repo_root}, helper returned: {helper_repo_root}"
    