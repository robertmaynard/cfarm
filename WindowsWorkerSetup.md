How to setup a windows machine as a cfarm worker

CFarm requires machines to have a ssh daemon, git on the path and generally
offer a POSIX interface. Now for windows machines this is fairly hard thing
to do.

So to setup windows CFarm workers I do the following:

##OpenSSH##
I install an ssh server, currently I am using copssh ( https://www.itefix.no/i2/copssh )
which provides a very lightweight cygwin shell when remoting in.

Once copssh is setup, you will need to add the worker user name to the
authorized list of users allowed to log in. Next you will need to allow
the sshd executable access through the firewall, which you do by adding
it to the windows firewall program:
```
Windows FireWall
  ->Allow a Program Through
    ->Browse
    ->Add ICW/Bin/sshd
```

The version of copssh I setup was missing cygattr-1.dll, which can
be fixed by downloading:
```
cygwin.cybermirror.org/release/attr/libattr1/libattr1-2.4.43-1.tar.bz2
```
and placing the dll's into the Bin folder


##Git##
Next up is to properly expose git to the cygwin shell. If you have a different
openssh server, or are using a full cygwin shell you can most likely install
git through that.

In my case I have msysgit on the machine already and don't want a second
git. So all I did was copied git.exe from msysgit and dropped it into the
Bin folder of ICW. You will need to also copy libiconv-2.dll also to the Bin
folder for git to worker properly.


##Ninja##

Todo:


##MSVC Vars##

Todo:
http://fd-imaging.com/compiling-with-msvc-cygwin-and-qmake/
