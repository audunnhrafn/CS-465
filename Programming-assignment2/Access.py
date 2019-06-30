import cmd
from collections import defaultdict

ACCOUNTS_FILE = "accounts.txt"
AUDIT_FILE = "audit.txt"
GROUPS_FILE = "groups.txt"
FILES_FILE = "files.txt"

CURRENT_USER = ""
USERLIST = dict()
USERGROUPS = dict()
USERFILES = defaultdict(list)

AUDIT = open(AUDIT_FILE, 'w')

#Updates the file.txt file
def update_file():
    with open(FILES_FILE, 'w+') as f:
        f.seek(0)
        for key, item in USERFILES.items():
            info = key + ': ' + " ".join(item) + "\n"
            f.write(info)

#Updates the groups.txt file
def update_group():
    with open(GROUPS_FILE, 'w+') as g:
        g.seek(0)
        for key,item in USERGROUPS.items():
            info = key + ': ' + item + "\n"
            g.write(info)

#Updates the account.txt file
def update_account():
    with open(ACCOUNTS_FILE, 'w+') as a:
        a.seek(0)
        for key, item in USERLIST.items():
            info = key + " " + item + "\n"
            a.write(info)

#Takes in the username and password parameters and passes it into global userlist dict.
def useradd(username, password):
    USERLIST[username] = password
    print("User %s created" % username)
    AUDIT.write("User %s created\n" % username)


#Takes in username and password parameters and checks if the username and password are correct
#then makes the Current user variable be the correct logged in user.
def login(username, password):
    if username in USERLIST:
        if USERLIST[username] == password:
            global CURRENT_USER
            CURRENT_USER = username
            print("User %s logged in" % username)
            AUDIT.write("User %s logged in\n" % username)
        else:
            print("Login failed: invalid username or password")
            AUDIT.write("Login failed: invalid username or password\n")
    else:
        print("Login failed: invalid username or password")
        AUDIT.write("Login failed: invalid username or password\n")

#Takes the global current user variable and logs the user out by making it be a empty string
def logout():
    global CURRENT_USER
    print("User %s logged out" % CURRENT_USER)
    AUDIT.write("User %s logged out\n" % CURRENT_USER)
    CURRENT_USER = ""


#Creates a group by taking a groupname and matching it with the Usergroup global dict.
def groupadd(groupname):
    if groupname not in USERGROUPS:
        if groupname.lower() != 'nil':
            USERGROUPS[groupname] = ''
            print("Group %s created" % groupname)
            AUDIT.write("Group %s created\n" % groupname)
        else:
            print("Error: group name cannot be nil")
            AUDIT.write("Error: group name cannot be nil\n")
    else:
        print("Error: group %s already exists" % groupname)
        AUDIT.write("Error: group %s already exists\n" % groupname)


#Adds the spesific user to the group
def usergrp(username, groupname):
    s = USERGROUPS[groupname]
    s += username + " "
    USERGROUPS[groupname] = s
    print("User %s added to group %s" % (username, groupname))
    AUDIT.write("User %s added to group %s\n" % (username, groupname))


#Creates a new file with the default permissions and currently logged in user.
def mkfile(filename):
    if check_filename(filename) == False:
        print("Error: filename cannot be %s" % (filename))
        AUDIT.write("Error: filename cannot be %s" % (filename))
        return

    if filename not in USERFILES:
            #user, group, owner perm, group perm, other perm.
            fileinfo = [CURRENT_USER, 'nil', 'rw-', '---', '---']
            USERFILES[filename] = fileinfo
            #to create the file in the folder
            with open(filename, "w+") as a:
                pass
            print("File %s with owner %s and default permissions created" % (filename, CURRENT_USER))
            AUDIT.write("File %s with owner %s and default permissions created\n" % (filename, CURRENT_USER))
    else:
        print("Error: file %s already exists" % filename)
        AUDIT.write("Error: file %s already exists\n" % filename)


#updates the permissions for each group
def chmod(filename, owner, group, other):
    if check_filename(filename) == False:
        print("Error: filename cannot be %s" % (filename))
        AUDIT.write("Error: filename cannot be %s" % (filename))
        return

    if filename in USERFILES:
        if USERFILES[filename][0] == CURRENT_USER or CURRENT_USER == 'root':
            USERFILES[filename][2] = owner
            USERFILES[filename][3] = group
            USERFILES[filename][4] = other
            print("Permissions for %s set to %s %s %s by %s" % (filename, owner, group, other, CURRENT_USER))
            AUDIT.write("Permissions for %s set to %s %s %s by %s\n" % (filename, owner, group, other, CURRENT_USER))
        else:
            print("Error with chmod: %s does not have the permission to change %s" % (CURRENT_USER, filename))
            AUDIT.write("Error with chmod: %s does not have the permission to change %s\n" % (CURRENT_USER, filename))
    else:
        print("Error with chmod: file %s not found" % (filename))
        AUDIT.write("Error with chmod: file %s not found\n" % (filename))


#Changes the owner of the file
def chown(filename, username):
    if check_filename(filename) == False:
        print("Error: filename cannot be %s" % (filename))
        AUDIT.write("Error: filename cannot be %s" % (filename))
        return

    if filename in USERFILES:
        USERFILES[filename][0] = username
        print("Owner of %s changed to %s" % (filename, username))
        AUDIT.write("Owner of %s changed to %s\n" % (filename, username))
    else:
        print("Error with chown: file %s not found" % (filename))
        AUDIT.write("Error with chown: file %s not found\n" % (filename))

#changes the groupname to something else if he has a permission to do that
def chgrp(filename, groupname):
    if check_filename(filename) == False:
        print("Error: filename cannot be %s" % (filename))
        AUDIT.write("Error: filename cannot be %s" % (filename))
        return

    if filename in USERFILES:
        if USERFILES[filename][1] == "nil":
            if CURRENT_USER == USERFILES[filename][0] or CURRENT_USER == "root":
                if CURRENT_USER in USERGROUPS[groupname] or CURRENT_USER == "root":
                    USERFILES[filename][1] = groupname
                    print("Group for %s changed to %s by %s" % (filename, groupname, CURRENT_USER))
                    AUDIT.write("Group for %s changed to %s by %s\n" % (filename, groupname, CURRENT_USER))
                else:
                    print("Error with chgrp: User %s is not a member of group %s" % (CURRENT_USER, groupname))
                    AUDIT.write("Error with chgrp: User %s is not a member of group %s\n" % (CURRENT_USER, groupname))
            else:
                print("Error with chgrp: User %s does not have the permission to change %s" % (CURRENT_USER, filename))
                AUDIT.write("Error with chgrp: User %s does not have the permission to change %s\n" % (CURRENT_USER, filename))
        else:
            print("Error: file %s already belongs to a group" % filename)
            AUDIT.write("Error: file %s already belongs to a group\n" % filename)
    else:
        print("Error with chgrp: file %s not found" % (filename))
        AUDIT.write("Error with chgrp: file %s not found\n" % (filename))


#helper function to read in the text of the file
def read_text(filename):
    with open(filename, 'r') as f:
        content = f.read()
    print("User %s reads %s as: %s" % (CURRENT_USER, filename, content))
    AUDIT.write("User %s reads %s as:\n %s" % (CURRENT_USER, filename, content))

#helper function to write a text to a file
def write_text(filename,text):
    text = " ".join(text)
    text += '\n'
    with open(filename, 'a') as f:
        f.write(text)
    print("User %s wrote to %s: %s" % (CURRENT_USER, filename, text))
    AUDIT.write("User %s wrote to %s: %s" % (CURRENT_USER, filename, text))


#reads in information if the correct permission is allowed
def read(filename):
    if check_filename(filename) == False:
        print("Error: filename cannot be %s" % (filename))
        AUDIT.write("Error: filename cannot be %s" % (filename))
        return

    if filename in USERFILES:
        file = USERFILES[filename]
        #owner
        if CURRENT_USER == file[0] and file[2][0] == 'r':
            read_text(filename)
        #group
        elif file[1] != 'nil' and CURRENT_USER in USERGROUPS[file[1]] and file[3][0] == 'r' and CURRENT_USER != file[0]:
            read_text(filename)
        #other
        elif file[4][0] == 'r' and CURRENT_USER != file[0] and CURRENT_USER not in USERGROUPS[file[1]]:
            read_text(filename)
        else:
            print("User %s denied read access to %s" % (CURRENT_USER, filename))
            AUDIT.write("User %s denied read access to %s\n" % (CURRENT_USER, filename))
    else:
        print("Error with read: file %s not found" % (filename))
        AUDIT.write("Error with read: file %s not found\n" % (filename))

#Writes out text if the correct permission is allowed
def write(filename, text):
    if check_filename(filename) == False:
        print("Error: filename cannot be %s" % (filename))
        AUDIT.write("Error: filename cannot be %s" % (filename))
        return

    if filename in USERFILES:
        file = USERFILES[filename]
        #owner
        if CURRENT_USER == file[0] and file[2][1] == 'w':
            write_text(filename, text)
        #group
        elif file[1] != 'nil' and CURRENT_USER in USERGROUPS[file[1]] and file[3][1] == 'w' and CURRENT_USER != file[0]:
            write_text(filename, text)
        #other
        elif file[4][1] == 'w' and CURRENT_USER != file[0] and CURRENT_USER not in USERGROUPS[file[1]]:
            write_text(filename, text)
        else:
            print("User %s denied write access to %s" % (CURRENT_USER, filename))
            AUDIT.write("User %s denied write access to %s\n" % (CURRENT_USER, filename))
    else:
        print("Error with write: file %s not found" % (filename))
        AUDIT.write("Error with write: file %s not found\n" % (filename))

#checks the permission to execute a file
def execute(filename):
    if check_filename(filename) == False:
        print("Error: filename cannot be %s" % (filename))
        AUDIT.write("Error: filename cannot be %s" % (filename))
        return

    if filename in USERFILES:
        file = USERFILES[filename]
        #owner
        if CURRENT_USER == file[0] and file[2][2] == 'x':
            print("File %s executed by %s" % (filename, CURRENT_USER))
            AUDIT.write("File %s executed by %s\n" % (filename, CURRENT_USER))
        #group
        elif file[1] != 'nil' and CURRENT_USER in USERGROUPS[file[1]] and file[3][2] == 'x' and CURRENT_USER != file[0]:
            print("File %s executed by %s" % (filename, CURRENT_USER))
            AUDIT.write("File %s executed by %s\n" % (filename, CURRENT_USER))
        #other
        elif file[4][2] == 'x' and CURRENT_USER != file[0] and CURRENT_USER not in USERGROUPS[file[1]]:
            print("File %s executed by %s" % (filename, CURRENT_USER))
            AUDIT.write("File %s executed by %s\n" % (filename, CURRENT_USER))
        else:
            print("User %s denied execute access to %s" % (CURRENT_USER, filename))
            AUDIT.write("User %s denied execute access to %s\n" % (CURRENT_USER, filename))
    else:
        print("Error with execute: file %s not found" % (filename))
        AUDIT.write("Error with execute: file %s not found\n" % (filename))

#shows the listing of a file and it's permissions
def ls(filename):
    if check_filename(filename) == False:
        print("Error: filename cannot be %s" % (filename))
        AUDIT.write("Error: filename cannot be %s" % (filename))
        return

    if filename in USERFILES:
        pri = filename
        for i in USERFILES[filename]:
            pri += " " + i
        print(pri)
        AUDIT.write(pri + "\n")
    else:
        print("Error with ls: file %s not found" % (filename))
        AUDIT.write("Error with ls: file %s not found\n" % (filename))

#ends the process and uploads data into files.
def end():
    AUDIT.close()
    update_account()
    update_file()
    update_group()

def check_filename(filename):
    if filename == ACCOUNTS_FILE or filename == GROUPS_FILE or filename == AUDIT_FILE or filename == FILES_FILE:
        return False
    return True

#command line helper
class Program(cmd.Cmd):

    prompt = ""

    def do_useradd(self, arg):
        user = arg.split()
        if CURRENT_USER == '' or CURRENT_USER == 'root':
            if user[0] not in USERLIST:
                useradd(user[0], user[1])
            else:
                print("Error: user %s already exists" % user[0])
                AUDIT.write("Error: user %s already exists\n" % user[0])
        else:
            print("Error: only root may issue useradd command")
            AUDIT.write("Error: only root may issue useradd command\n")

    def do_login(self, arg):
        user = arg.split()
        if CURRENT_USER == "":
            login(user[0], user[1])
        else:
            print("Login failed: simultaneous login not permitted")
            AUDIT.write("Login failed: simultaneous login not permitted\n")

    def do_logout(self, arg):
        if CURRENT_USER != "":
            logout()
        else:
            print("Logout failed: must be logged in to logout")
            AUDIT.write("Logout failed: must be logged in to logout\n")

    def do_groupadd(self, arg):
        if CURRENT_USER == 'root':
            groupadd(arg)
        else:
            print("Error: only root may issue groupadd command")
            AUDIT.write("Error: only root may issue groupadd command\n")

    def do_usergrp(self, arg):
        userg = arg.split()
        if CURRENT_USER == "root":
            if userg[1] in USERGROUPS:
                usergrp(userg[0], userg[1])
            else:
                print("Error: %s does not exist" % userg[1])
                AUDIT.write("Error: %s does not exist\n" % userg[1])
        else:
            print("Error: only root may issue usergrp command")
            AUDIT.write("Error: only root may issue usergrp command\n")

    def do_mkfile(self, arg):
        if CURRENT_USER != "":
            mkfile(arg)
        else:
            print("Error: user must be logged in to issue mkfile command")
            AUDIT.write("Error: user must be logged in to issue mkfile command\n")

    def do_chmod(self, arg):
        com = arg.split()
        if(CURRENT_USER != ""):
            chmod(com[0], com[1], com[2], com[3])
        else:
            print("Error: user must be logged in to issue chmod command")
            AUDIT.write("Error: user must be logged in to issue chmod command\n")

    def do_chown(self, arg):
        com = arg.split()
        if CURRENT_USER == "root":
            chown(com[0], com[1])
        else:
            print("Error: only root may issue chown command")
            AUDIT.write("Error: only root may issue chown command\n")

    def do_chgrp(self, arg):
        com = arg.split()
        if CURRENT_USER != "":
            chgrp(com[0], com[1])
        else:
            print("Error: user must be logged in to issue chgrp command")
            AUDIT.write("Error: user must be logged in to issue chgrp command\n")

    def do_read(self, arg):
        if CURRENT_USER != "":
            read(arg)
        else:
            print("Error: user must be logged in to issue read command")
            AUDIT.write("Error: user must be logged in to issue read command\n")

    def do_write(self, arg):
        com = arg.split()
        if CURRENT_USER != "":
            write(com[0], com[1:])
        else:
            print("Error: user must be logged in to issue write command")
            AUDIT.write("Error: user must be logged in to issue write command\n")

    def do_execute(self, arg):
        if CURRENT_USER != "":
            execute(arg)
        else:
            print("Error: user must be logged in to issue execute command")
            AUDIT.write("Error: user must be logged in to issue execute command\n")

    def do_ls(self, arg):
        if CURRENT_USER != "":
            ls(arg)
        else:
            print("Error: user must be logged in to issue ls command")
            AUDIT.write("Error: user must be logged in to issue ls command\n")

    def do_end(self, line):
        end()
        return True

if __name__ == '__main__':
    prog = Program()
    prog.cmdloop()
