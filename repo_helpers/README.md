This is a python package, that is used throughout mutliple repositories for automation.  
The goal is to have a single script, on top of which I can write smaller automation scripts. With the least amount of dependencies 

Usage:
'''
from repo_helpers.Repo_Helper import Repo_Helper as docktools
helper = docktools()
helper.build_image()
'''