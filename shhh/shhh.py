import argon2
from cryptography.fernet import Fernet
import base64
import json
import copy
import pyperclip
import hashlib

class Shhh():

    def __init__(self):

        self.options = []
        self.options.append("List all passwords")
        self.options.append("Add new password")
        self.options.append("Get password")
        self.key = None
        self.encryptor = None
        self.library = None

    def setup(self, library=None, master_pass=None):
        """
        Init the Shhh class with a key and the ability to encrypt and whatnot.
        self.cipher is the Fernet encryption stuff.
        :param key:
        """

        # Load the credential library selected, or load the default library.

        if library == None:
            print("No library chosen, attempting to load default library")
            try:
                self.load_library("default.json")
            except Exception as e:
                print("Could not load library!")
                quit(0)

        # Ask the user for the library password.

        if master_pass == None:
            print("Enter the master password for this library.")
            master_pass: str = input(" - ")

        # Check they entered the password by comparing it to the hash of the key used to encrypt (library["key_thumbprint"])
        # Quit if invalid.

        if not self.check_valid_key(master_pass):
            print("Incorrect password.")
            quit()

        # Probably can incorporate this up earlier, generate the key from the password using Argon2 (look below).
        self.key = self.generate_key_from_password(master_pass)


        # Set up the cryptography fernet library.
        self.encryptor = Fernet(self.key)

    def load_library(self, library_path):
        """
        This will load a selected library.
        :param library_path:
        :return:
        """
        with open(library_path, 'r') as library_file:
            self.library = json.load(library_file)


    def create_library(self, path=None, salt=None, master_pass=None):
        """
        This will create a new library with a set of user parameters such as the salt.
        The user will be asked to enter the password they would like to use.
        A hash of the key derived from this password is also stored in the library to check if the user has entered the
        correct key.
        :param path:
        :param salt:
        :param master_pass:
        :return:
        """
        if salt == None:
            print("Enter the salt for the new library.")
            salt = input(" - ")

        if master_pass == None:
            print("Enter the password for the new library.")
            passwd = input(" - ")

        # Create the library, including generating the key thumbprint.
        library = {
            "version": "1.0",
            "salt": salt,
            "key_thumbprint": self.calculate_key_thumbprint(self.generate_key_from_password(passwd, salt=salt)),
            "credentials": []

        }

        # If the user sets no path just create a default library.
        if path==None:
            print("Creating library 'default.json'")
            with open("default.json", "w") as library_file:
                json.dump(library, library_file)

    def update_library(self):
        """
        TODO change this to work with password libraries that have different names.
        :return:
        """
        with open('./default.json', 'w') as library_file:
            json.dump(self.library, library_file)

    def generate_key_from_password(self, master_pass, salt=None):
        """
        Use argon2 to generate a key from the password.
        :param master_pass:
        :param salt:
        :return:
        """
        # If there is an error trying to open self.library it probably means that this function is being called
        # to create a new library. If that fails then no salt was entered (or an error in Argon2 popped up).
        try:
            key = argon2.low_level.hash_secret_raw(master_pass.encode(), self.library["salt"].encode(), time_cost=1, memory_cost=100000, parallelism=32, hash_len=64, type=argon2.low_level.Type.I)
        except Exception:
            if salt != None:
                key = argon2.low_level.hash_secret_raw(master_pass.encode(), salt.encode(), time_cost=1, memory_cost=100000, parallelism=32, hash_len=64, type=argon2.low_level.Type.I)
            else:
                print("No Salt Entered! Bye!")
                quit()
        encoded_key = base64.urlsafe_b64encode(key[:32])
        return encoded_key


    # Calculate the sha256 value of the key. Yeah, it's not really a thumbprint, but meh.
    def calculate_key_thumbprint(self, key):
        thumbprint = hashlib.sha3_256(key).hexdigest()
        return thumbprint

    def check_valid_key(self, password):
        """
        Compares the thumbprints of the lib key and the entered key and returns true/false depending on the match.
        :param password:
        :return:
        """
        input_key_thumb = self.calculate_key_thumbprint(self.generate_key_from_password(password))
        lib_key = self.library["key_thumbprint"]

        if input_key_thumb == lib_key:
            return True
        else:
            return False

    def interact(self):
        """
        The meat and potatoes that does stuff.
        :return:
        """
        while True:
            self.show_options()
            option = input(":")
            if int(option) == 1:
                cred = self.encrypt_credential()
                self.library["credentials"].append(cred)
                self.update_library()
            if int(option) == 2:
                self.decrypt_all()

    def show_options(self):
        """
        Shows available options.
        :return:
        """
        for key, option in enumerate(self.options):
            print(str(key)+" "+option)

    def encrypt_credential(self):
        """
        Encrypts a credential. Have to remember that it's base64 encoded...
        :return:
        """
        print("Enter the name of the credential")
        cred_name = input("Cred Name: ")
        print("Enter the credential username.")
        username = input("Username: ")
        print("Enter the account password: ")
        password = input("Password: ")
        enc_pass = self.encryptor.encrypt(password.encode())

        cred = {
            "name": cred_name,
            "usrnm": username,
            "pwd": enc_pass.decode("utf-8")
        }

        print(enc_pass.decode("utf-8"))

        return cred

    def decrypt_all(self):
        """
        Only for lazy testing.
        :return:
        """
        for credential in self.library["credentials"]:
            credential = copy.deepcopy(credential)
            decrypted_pass = self.encryptor.decrypt(credential["pwd"].encode())
            print(decrypted_pass)

default_config = {
    "library_dir_name": "libraries",
    "default_library_name": "default",
    "encrypt_usernames": True,
    "password_rules": {
        "min_length": 8,
        "special_chars": False,
        "upper_case": False
    }
}