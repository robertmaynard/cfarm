### CFarm ###

CFarm goal is to keep numerous machines in sync when developing cross platform
C++ projects. You can think of a private continuous testing, without any fancy
reporting, user interface, or other 'features' that other tools have.


## Reason ##

The standard problem I have is when developing on a single platform,
I introduce subtle cross platform breaking code, things like using
c99 types, or using a C++11 method from stl.

Now I can commit these breaks, and send the branch for review where
it will get sniffed out and reported, but the turnaround for that is
incredibly high.

Likewise I generally switch between machines to replicate these breaks,
and every time I do that I need to recheck out the code and generally go
through the entire configuration, compilation, test process.


## Setup Development Machine ##

To use cfarm you need a setup a configuration per project. This is
done by creating a .cfarm folder in the root of your git repo that
you want cfarm to work on (Yes cfarm only supports git, I said cfarm
has no features).

The folder will look something like:

```
.cfarm/
  - metaverse.cdep
  - deliverator.cdep
  - bigboard.cdep
```

Each .cdep file will describe how to deploy the project to a machine.
Each file name is the cfarm workers name, allowing you to have multiple workers
that point to the same physical machine. Here is an example .cdep file:

```
{
"hostname" : "bigboard",
"user" : "hiro",
"cpp_compiler" : "/usr/bin/g++-4.6",
"src_location" : "/home/hiro/Work/bigboard/src",
"build_location" : "/home/hiro/Work/bigboard/build",
"build_generator" : "Ninja",
"build_flags" : "-j8"
}
```

Here is a list of required settings for a .cdep file:
- hostname = computer name, or ip address of worker
- user = the user we are going to log in as
- src_location = the location to store the source for the current project
- build_location = the location to build the project
- build_generator = the CMake generator to use for building.
All CMake generators are currently supported. For Generators like Visual Studio
you will also need to specify the option build_configuration option.

Here is a list of optional settings for a .cdep file:
- cmake_location : the location of the cmake binary
- c_compiler : Absolute path to the c compiler
- cpp_compiler : Absolute path to the c++ compiler
- cuda_compiler : Absolute path to the cuda compiler
- cuda_host_compiler : Absolute path to the cuda host compiler
- \<lang\>_flags : default flags for the C/C++/CUDA language
- library_type : State if you want to build Statically or Shared.
- build_flags = list of flags for compilation, generally holds '-j<N>'
- build_configuration = Explicitly state the build configuration type
to use such as Debug, or Release. Needed when you are using multi
configuration generators like Visual Studio.

Here are example of all the optional settings:

```
"c_compiler" : "/usr/bin/gcc-4.8",
"cpp_compiler" : "/usr/bin/g++-4.8",
"library_type" : "Shared",
"build_flags" : "-j8",
"build_configuration" : "Debug"
```

## How to use CFarm ##

cfarm understands the concepts of setup, build, and test.

The Setup command looks like:

```
cfarm setup metaverse
```

As it only supports setting up machines one by one. This is required as we
currently launch ccmake on the machine to allow you to configure the starting
building options. Todo: Allow the user to resetup a machine to switch just
configure options

The build and test command have three ways to be called:

```
 cfarm build all
 cfarm build deliverator
 cfarm build d*

 cfarm test all
 cfarm test bigboard metaverse
 cfarm test b* meta*

```

cfarm also allows you to sent options down to the workers at build
and test time, it does this by sending all arguments passed after the
first '--' down to the command line.

So to specify a specific target for all workers to build you would use the
following command line:

```
cfarm build all -- --target Sword
```

To specify to run tests that match a ctest regular expression you would
use:

```
cfarm test all -- -R UnitTestSword
```

## CFarm and Git-LF S##

cfarm has support for handling repositories that use Git-LFS. Basically
LFS doesn't support pushing data to remotes that don't support LFS which
covers all cfarm workers. So instead what we do is push the data to a
thirdparty server.

This is done on a per project basis by adding a ``lfs.config`` file to
the .cfarm folder

```
.cfarm/
  - metaverse.cdep
  - deliverator.cdep
  - bigboard.cdep
  - lfs.config
```

This file will look like:

```
{
"push_url" : "git@github.com:github.com/user/repo.git",
"fetch_url" : "https://www.github.com/user/repo.git"
}
```

## Requirements ##

```
Python 2.6 or 2.7
Fabric
```

