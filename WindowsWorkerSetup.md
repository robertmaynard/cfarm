##How to setup a Windows cfarm worker##

cfarm requires machines to have a ssh daemon, git and cmake on the path and generally
offer a POSIX interface. Now for windows machines this is requires some setup.

So to setup windows farm workers I do the following:

##OpenSSH##
You will need to install an ssh server, currently I am using freeSSHD ( http://www.freesshd.com )
which allows you to setup a custom login. Make sure to copy your public
key into the authentication folder, and create a user account
that only can be accessed with public/private key instead
of password.

To get the user's public key to properly be detected by freeSSD you
need to copy the public key file to the authentication folder and rename
it to be the name of the user, and the file should have no extension.

You will need to make sure that the user that is running the sshd dameon
has adminstrator rights, or manaully launch the server as admin.

##Shell##

My recommendation is to drop the cmd.exe default for freeSSHD and
instead set the shell to be:
```
C:\Windows\SysWOW64\cmd.exe /c ""C:\Program Files (x86)\Git\bin\sh.exe" --login"
```

This will give

##Git##
Since you changed your shell to be sh.exe you don't need to do anything
else here.

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
