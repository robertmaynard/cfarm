##How to setup a Windows cfarm worker##

cfarm requires machines to have a ssh daemon, git and cmake on the path and generally
offer a POSIX interface. Now for windows machines this is requires some setup.

So to setup windows farm workers I do the following:

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

We do this over setting up a bash_rc alias as aliases are not currently executed
as we don't use an interactive shell

##CMake##

Make sure that cmake is on the path, I do this creating modifying my
bash_rc file to extend my path variable:
```
export PATH=$PATH:/cygdrive/c/Program\ Files\ \(x86\)/CMake\ 2.8/bin/
```

##Ninja##

Make sure that ninja is on the path, I do this creating modifying my
bash_rc file to extend my path variable:
```
export PATH=$PATH:/cygdrive/c/ninja/bin/
```

##MSVC Vars##

The current issue is that everything to setup msvc requires us to run
something each time we log in. What we need to do is create some template
files that convert the vc env settings to bash settings. The other
options is somehow writing our own prompt that will set the proper 
env flags before forwarding to bash.


See the following for more info on setting up msvc inside cygwin:
http://doc36.controltier.org/wiki/CopSSH_(windows)
http://stackoverflow.com/questions/366928/invoking-cl-exe-msvc-compiler-in-cygwin-shell
http://fd-imaging.com/compiling-with-msvc-cygwin-and-qmake/
