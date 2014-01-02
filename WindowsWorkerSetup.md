##How to setup a Windows cfarm worker##

cfarm requires machines to have a ssh daemon, git and cmake on the path and generally
offer a POSIX interface. Now for windows machines this is requires some setup.

So to setup windows farm workers I do the following:

##OpenSSH##
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


##Shell##

My recommendation is to drop the cmd.exe default for freeSSHD and
instead set the shell to be:
```
C:\Windows\SysWOW64\cmd.exe /c ""C:\Program Files (x86)\Git\bin\sh.exe" --login"
```

This will give

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

Make sure that cmake is on the path, I do this by extending my
login users path like so:
```
export PATH=$PATH:/cygdrive/c/Program\ Files\ \(x86\)/CMake\ 2.8/bin/
```

##Ninja##

Make sure that ninja is on the path, I do this by extending my
login users path like so:
```
export PATH=$PATH:/cygdrive/c/ninja/bin/
```

##MSVC Vars##

Depending on the generator you want to use on windows we
have different issues with invoking it from the command line.


###Visual Studio Generators###

This work is still under development

The first is we need the ability to state in cfarm for generators that are
multi configurations what the default configuration should be.
The best way to solve that is to add more syntax options to the generator list:

```
"build_generator" : "Visual Studio 10 Win64 Debug"
```

This will tell cfarm that when issuing the cmake --build command
we should explicitly state the --config option to be set to Debug.


###Ninja Generator###

For the Ninja generator we need a way to tell the shell how to
get the proper visual studio enviornment variables. Currently
I don't know of a way to get this to work seemlessly inside cfarm.

### With Copssd ###



### With FreeSSH###
Instead what we can do is setup a freeSSHD to have a given
visual studio compiler enviornment loaded. While this isn't perfect
since we can't give each user a shell, it is a good start.

For example to get a Visual Studio 2008 x64 shell you would
create a batch file with the following:
```
call "%VS90COMNTOOLS%..\..\VC\vcvarsall.bat" amd64 >NUL;
%comspec% /k ""C:\Program Files (x86)\Git\bin\sh.exe"" --login
```

And set the freesshd shell to:
```
C:\Windows\SysWOW64\cmd.exe /c ""D:\vs2009_32.bat""
```


See the following for more info on setting up msvc inside a shell:
http://stackoverflow.com/questions/366928/invoking-cl-exe-msvc-compiler-in-cygwin-shell
