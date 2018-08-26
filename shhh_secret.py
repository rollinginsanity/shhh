from shhh.shhh import Shhh
import os.path

"""
This is meant to be the startup script to run the password manager. Doesn't do much yet. All it does is check if the 
default library is there. I should probably use a dedicated extension, and let the user pick which file they are using.
"""

shhh = Shhh()

if os.path.isfile("./default.json"):

    shhh.setup()
    print(shhh.library)

else:
    shhh.create_library()



