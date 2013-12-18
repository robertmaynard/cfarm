###CFarm###

CFarm is a small project to help people develop cross platform c++ code. By allowing them to build and test code on remote machine quickly


##Reason##

The standard problem I have is when developing on a single platform,
I introduce subtle cross platform breaking code, things like using
c99 types, or using a C++11 method from stl.

Now I can commit these breaks, and send the branch for review where
it will get sniffed out and reported, but the turnaround for that is
incredibly high.

Likewise I generally switch between machines to replicate these breaks,
and every time I do that I need to recheck out the code and generally go
through the entire configuration, compilation, test process.

The goal of cfarm is to keep numerous machines in sync when developing
on a project. You can think of a private continuous testing, without any fancy
reporting, user interface, or other 'features' that other tools have.

##Setup Development Machine##

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
- build_generator = the cmake generator to use for building ( Make, Ninja, MSVC, ...)

Here is a list of optional settings for a .cdep file:
- build_flags = list of flags for compilation, generally holds -j<N>
- env_setup = path to a file we should run whenever we log into the remote
              machine. This can be used to setup env flags, load the
              proper modules, or setup vcvarsall.bat on windows machines.

##How to use cfarm##

cfarm understands the concepts of setup, build, and test.

The Setup command looks like:

```
cfarm setup metaverse
```

As it only supports setting up machines one by one. This is required as we
currently launch ccmake on the machine to allow you to configure the starting
building options. Todo: Allow the user to resetup a machine to switch just
configure options

The build and test command have two ways to be called:

```
 cfarm build all
 cfarm build deliverator

 cfarm test all
 cfarm test bigboard metaverse
```


##What cfarm is doing##

When you call setup cfarm ssh's in to the remote machine and enters the
source directory where it will create a git repo with an explicit working
tree. We than configure a post_recieve hook that sets up the working directory
and updates / inits all submodules. This setup means that we can always push
commits without worry, and can send patches easily to the machine.

Next setup will push the master branch of your repository to the machine
you have setup.

Lastly we open a remote connection to the machine, move into the build
directory and invoke ccmake so that you can configure the build directory.

When you call build, cfarm does the following:
  1. finds the remotes you requested and pushes the commits to those machines
     this triggers the remote to checkout that code
  2. ssh into the machine and run cmake --build -- ${build-flags}
Todo: we need to be able to flag that a remote machine has finished checking
out the code we pushed before we try build.

##Requirements##

```
Python 2.6 or 2.7
Fabric
```



