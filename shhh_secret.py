from shhh.shhh import Shhh
from os import path, getcwd, makedirs
import json


"""
This is meant to be the startup script to run the password manager. Doesn't do much yet. All it does is check if the 
default library is there. I should probably use a dedicated extension, and let the user pick which file they are using.
"""

shhh = Shhh()

if not path.isfile("./config.json"):
    config = {}
    # First Time Setup
    from shhh.shhh import default_config
    print("Performing first time setup!")
    base_path: str = getcwd() + "/" # Base path that the script will run from.
    print("Base path will be: "+base_path)
    # Create directory for password libraries.
    lib_dir = input("What folder do you want to store passwords in? ["+base_path+default_config["library_dir_name"]+"]")
    # Use default if user does not enter a value.
    print(len(lib_dir))
    if len(lib_dir) < 1:
        lib_dir = base_path+default_config["library_dir_name"]
        print("Defaulting library directory set to: "+lib_dir)
    else:
        lib_dir = base_path+lib_dir
        print("Library directory set to: " + lib_dir)

    if not path.exists(lib_dir):
        print("Folder does not exist, creating folder now.")
        makedirs(lib_dir)
    else:
        print("Directory already exists.")

    config["libraries_path"] = lib_dir

    with open("./config.json", 'w') as config_file:
        json.dump(config, config_file)

if path.isfile("./default.json"):

    shhh.setup()
    print(shhh.library)
    shhh.interact()
else:
    shhh.create_library()



