#! /usr/bin/env python3

import os, sys, re

pid = os.getpid()

while 1:
    os.write(1,("$").encode())
    cmd = os.read(0, 50).decode().strip()
    if(cmd == "exit"):
        break

    rc = os.fork()

    if rc < 0:
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)

    elif rc == 0: #Child
        os.write(1, ("Child: My pid==%d.  Parent's pid=%d\n" % 
                 (os.getpid(), pid)).encode())
        args = cmd.split(" ")
        for i in range(len(args)-1):
            if(args[i]==">"):
                os.close(1)
                fa = str(os.open(args[i+1], os.O_WRONLY | os.O_CREAT))
                os.set_inheritable(1, True)
                n = len(args)
                for j in range(0, n-i):
                    args.pop()
        for dir in re.split(":", os.environ['PATH']): # try each directory in the path
            program = "%s/%s" % (dir, args[0])
            os.write(1, ("Child:  ...trying to exec %s\n" % program).encode())
            try:
                os.execve(program, args, os.environ) # try to exec program
            except FileNotFoundError:             # ...expected
                pass                              # ...fail quietly
        os.write(2, ("Child:    Could not exec %s\n" % args[0]).encode())
        sys.exit(1)                 # terminate with error

    else:                           # Parent (forked ok)
        os.write(1, ("Parent: My pid=%d.  Child's pid=%d\n" % 
                    (pid, rc)).encode())
        childPidCode = os.wait()
        os.write(1, ("Parent: Child %d terminated with exit code %d\n" % 
                    childPidCode).encode())
