#! /usr/bin/env python3

import os, sys, re

pid = os.getpid()

while 1:
    os.write(1,("$").encode())
    cmd = os.read(0, 100).decode().strip()
    args = cmd.split(" ")
    piped = False
    args2 = []
    if(len(cmd)==0):
        pass
    elif(args[0] == "exit"):
        break
    elif(args[0]=="cd"):
        os.chdir(args[1])
    else:

        for i in range(len(args)-1):
            if(args[i]=="|"):
                piped = True
                n = len(args)
                for j in range(0, n-i):
                    args2.append(args.pop())
                args2.pop()
                args2.reverse()
                pr,pw = os.pipe()
                for f in (pr, pw):
                    os.set_inheritable(f, True)
                break

        rc = os.fork()

        if rc < 0:
            os.write(2, ("fork failed, returning %d\n" % rc).encode())
            sys.exit(1)

        elif rc == 0: #Child
            if(piped):
                os.close(1)                 # redirect child's stdout
                os.dup(pw)
                for fd in (pr, pw):
                    os.close(fd)
                os.set_inheritable(1, True)
            else: 
                for i in range(len(args)-1):
                    if(args[i]==">"): #output redirection
                        os.close(1)
                        fa = str(os.open(args[i+1], os.O_WRONLY | os.O_CREAT))
                        os.set_inheritable(1, True)
                        n = len(args)
                        for j in range(0, n-i):
                            args.pop()
                        break

            for dir in re.split(":", os.environ['PATH']): # try each directory in the path
                program = "%s/%s" % (dir, args[0])
                try:
                    os.execve(program, args, os.environ) # try to exec program
                except FileNotFoundError:             # ...expected
                    pass                              # ...fail quietly
            os.write(2, ("Child:    Could not exec %s\n" % args[0]).encode())
            sys.exit(1)                 # terminate with error

        else:                           # Parent (forked ok)

            if(piped):
                rc2 = os.fork()
                if rc2 < 0:
                    os.write(2, ("fork failed, returning %d\n" % rc).encode())
                    sys.exit(1)

                elif rc2 == 0: #Child
                    os.close(0)
                    os.dup(pr)
                    for fd in (pw, pr):
                        os.close(fd)
                    os.set_inheritable(0, True)
                    for dir in re.split(":", os.environ['PATH']): # try each directory in the path
                        program = "%s/%s" % (dir, args2[0])
                        try:
                            os.execve(program, args2, os.environ) # try to exec program
                        except FileNotFoundError:             # ...expected
                            pass                              # ...fail quietly
                    os.write(2, ("Child2:    Could not exec %s\n" % args2[0]).encode())
                    sys.exit(1)
                else:
                    if(not cmd[len(cmd)-1]=="$"):
                        childPid2Code = os.wait()

            elif(not cmd[len(cmd)-1]=="$"):
                childPidCode = os.wait()
