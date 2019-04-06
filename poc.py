import argon2
from cryptography.fernet import Fernet
import base64
import json
import copy
import pyperclip

def setup():

    print("Enter the password: ")
    master_pass = input(" - ")

    key = argon2.low_level.hash_secret_raw(master_pass.encode("utf-8"), "blahblahblahblahblahblahblahblah".encode("utf-8"), time_cost=1, memory_cost=100000, parallelism=32, hash_len=64, type=argon2.low_level.Type.I)

    encoded_key = base64.urlsafe_b64encode(key[:32])

    print(encoded_key)

    encryptor = Fernet(encoded_key)

    return encryptor


def create_credential(encryptor):
    print("Enter the name of the credential")
    cred_name = input("Cred Name: ")
    print("Enter the credential username.")
    username = input("Username: ")
    print("Enter the account password: ")
    password = input("Password: ")

    cred = {
        "name": cred_name,
        "usrnm": username,
        "pwd": encryptor.encrypt(password.encode())
    }

    return cred

def decrypt_credential(credential, encryptor):
    credential = copy.deepcopy(credential)
    decrypted_pass = encryptor.decrypt(credential["pwd"])
    credential["pwd"] = decrypted_pass.decode()

    return credential

def to_clipboard(password):
    pyperclip.copy(password)
    print("Copied the password to the clipboard!")


encryptor = setup()

cred = create_credential(encryptor)

decrypted_cred = decrypt_credential(cred, encryptor)
print(cred)
print(decrypted_cred)
print(decrypted_cred["pwd"])
to_clipboard(decrypted_cred["pwd"])