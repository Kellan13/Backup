from datetime import datetime
import settings
import os
import time


class Log:
    def __init__(self):
        pass

    def get_time(self, formal=False):
        now = datetime.now()
        date = [str(now.month), str(now.day), str(now.year)]
        time_str = [str(now.hour), str(now.minute)]
        if formal:
            return '/'.join(date) + " " + ":".join(time_str)
        return ''.join(date) + ''.join(time_str)


class Files:
    def __init__(self, name, path=''):
        self.name = name
        try:
            filename = open(self.name, path + "x")
            filename.close()
        except FileExistsError:
            pass


class CopyFiles:
    def __init__(self):
        os.system("mkdir temp")
        self.log = Log()
        self.error_file = Files("error.txt", path='temp/')
        self.log_file = Files("log.txt", path='temp/')
        self.copy_list = []

    def backup(self):
        os.system("mkdir temp/Backup")
        s = settings.Settings()
        with open("copylist", "r") as f:
            for i in f:
                self.copy_list.append(i[:len(i)-1:])
        for i in self.copy_list:
            command = "cp" + i + "temp/Backup/ 2>> error.txt"
            os.system(command)
            time.sleep(.5)
        with open("log.txt", "w") as f:
            f.write("Back up created at " + self.log.get_time(formal=True))
        current_time = self.log.get_time()
        os.system("tar -cjvf " + current_time + ".tar.bz2 temp/")
        location = s.get_location()
        os.system("cp " + current_time + ".tar.bz2 " + location)
        os.system("rm -R temp/*")


def main():
    setup = settings.Settings()
    copy = CopyFiles()
    verification = False
    if setup.get_setup():
        try:
            with open("verification", "r") as f:
                verification_string = f.readline()
            if setup.check_verification(verification_string):
                verification = True
            else:
                raise FileNotFoundError
        except FileNotFoundError:
            os.system("echo 'problem verifying backup location' > error.txt")
            exit(1)
    if verification:
        copy.backup()


if __name__ == '__main__':
    main()
