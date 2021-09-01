import sys
import backup
import base64
import getpass
import json
import random
import string
from datetime import datetime

# commands = ["on", "off", "setup", "add", "remove", "run"]
# settings = ["username", "email", "location"]


class Encryption:
    def __init__(self):
        pass

    def scramble(self, string, key):  # Code is pulled from a kalle halden youtube video
        enc = []
        for i in range(len(string)):
            key_c = key[i % len(key)]
            enc.append(chr((ord(string[i]) + ord(key_c)) % 256))
        rtn = base64.urlsafe_b64encode("".join(enc).encode()).decode()
        return rtn

    def unscramble(self, string, key):
        dec = []
        rtn = base64.urlsafe_b64decode(string).decode()
        for i in range(len(string)):
            key_c = key[i % len(key)]
            dec.append(chr((256 + ord(rtn[i]) - ord(key_c)) % 256))
        rtn = rtn.join(dec)
        return rtn


class Settings:
    def __init__(self):
        self.settings_file = None
        self.settings_data = None
        self.encryption = Encryption()
        try:
            with open("settings.json", "r") as settings_file:
                self.settings_data = json.loads(settings_file.read())
        except FileNotFoundError:
            settings_data = {
                'username': '',
                'unlock_key': '',
                'status': False,
                'location': '',
                'verification': '',
                'setup': ''
            }
            j_object = json.dumps(settings_data, indent=4)
            with open("settings.json", "w") as f:
                f.write(j_object)
        except json.JSONDecodeError:
            print("There was an issue reading the settings file, please try again later")
            exit(1)

    def setup(self):
        print("Setup can only be done once. At anytime you can press Ctrl+c to leave setup program")
        try:
            if not self.settings_data:
                self.settings_data["setup"] = True
                username = self.username()
                location = self.location()
                self.settings_data["username"] = username
                self.settings_data["location"] = location
                self.set_verification(location)
                self.settings_data["unlock_key"] = self.encryption.scramble(username, self.password())
                self.update()
        except KeyboardInterrupt:
            pass

    def get_setup(self):
        return self.settings_data["status"]

    def change(self, setting, new):
        unlock = self.encryption.unscramble(self.settings_data["unlock_key"], input("Please enter your password: "))
        if unlock == self.settings_data["username"]:
            if setting == "password":
                new_password = self.password()
                self.settings_data["unlock_key"] = self.encryption.scramble(self.settings_data["username"], new_password)
            elif setting == "username":
                self.settings_data["username"] = new
            elif setting == "location":
                self.settings_data["location"] = new
                self.set_verification(new)
            elif setting == "status":
                self.settings_data["status"] = new
            else:
                print("Error changing setting")
        else:
            print("Incorrect password")

    def password(self):
        password1 = getpass.getpass("Please Enter a password: ")
        password2 = getpass.getpass("Please re-enter password: ")
        while password1 != password2:
            print("Passwords did not match, please try again")
            password1 = getpass.getpass("Please Enter a password: ")
            password2 = getpass.getpass("Please re-enter password: ")
        return password1

    def username(self):
        username = input("Enter a username: ")
        while len(username) == 0:
            username = input("Please enter a valid username: ")
        return username

    def location(self):
        location = input("Please enter the location to backup files to: ")
        while len(location) == 0:
            location = input("Please enter a valid location: ")
        return location

    def get_location(self):
        return self.settings_data["location"]

    def set_verification(self, location):
        random.seed(datetime.microsecond)
        rand_string = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
        self.settings_data["verification"] = rand_string
        with open("verification", "w") as f:
            f.write(rand_string)

    def check_verification(self, verification_string):
        check = self.settings_data["verification"]
        if check == verification_string:
            return True
        return False

    def update(self):
        with open("settings.json", "w") as f:
            f.write(json.dumps(self.settings_data, indent=4))


class Copy:
    def __init__(self):
        self.copy_data = []
        try:
            with open("copylist", "r") as f:
                for i in f:
                    self.copy_data.append(i[:len(i)-1:])
        except FileNotFoundError:
            f = open("copylist", "x")
            f.close()

    def add(self, new):
        if len(new) > 0:
            self.copy_data.append(new)
        else:
            print("Please enter a valid location")
        self.update()

    def remove(self, file_loc):
        if file_loc in self.copy_data:
            self.copy_data.pop(self.copy_data.index(file_loc))
        else:
            print("File does not exist in database")
        self.update()

    def update(self):
        for i in range(len(self.copy_data)):
            self.copy_data[i] += '\n'
        with open("copylist", "w") as f:
            f.writelines(self.copy_data)


def main():
    setting = Settings()
    copy = Copy()
    if sys.argv[1] == "on":
        if setting.get_setup():
            setting.change("status", True)
        else:
            setting.setup()
    elif sys.argv[1] == "off":
        setting.change("status", False)
    elif sys.argv[1] == "setup":
        if len(sys.argv) > 3:
            if sys.argv[2] == "username":
                setting.change("username", sys.argv[3])
            elif sys.argv[2] == "location":
                setting.change("location", sys.argv[3])
            elif sys.argv[2] == "password":
                setting.change("password", sys.argv[3])
            else:
                print("Improper use: Please enter the changed setting. Correct use: backup setup <setting> <new>")
        else:
            setting.setup()
    elif sys.argv[1] == "add":
        if len(sys.argv) == 3:
            copy.add(sys.argv[2])
        else:
            print("Improper use: Please provide a file location. Correct use: backup add <file location>")
    elif sys.argv[1] == "remove":
        if len(sys.argv) == 3:
            copy.remove(sys.argv[2])
        else:
            print("Improper use: File location does not exist in database. Correct use: backup add <file location>")
    elif sys.argv[1] == "run":
        program_backup = backup.CopyFiles()
        program_backup.backup()
    else:
        print("Improper use: type backup help for mor info")


if __name__ == "__main__":
    main()
