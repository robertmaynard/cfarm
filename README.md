This project is currently in design stage.

###CFarm###

CDeploy is a small project to help people develop cross platform c++ code
quickly, by allowing them to build and test code on remote machine quickly


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
on a project. You can think of a private continuous testing, without
about real reporting, and no UI, or features :)

##Setup##

To use cfarm you need a setup a configuration per project. This is
done by creating a .cfarm folder in the root of your git repo that
you want cfarm to work on (Yes cfarm only supports git, I said cfarm
has no features).

The folder will look something like:
.cfarm/
  - metaverse.cdep
  - deliverator.cdep
  - bigboard.cdep

Each .cdep file will describe how to deploy the project to a machine. This
entails the following

"ssh-key" : "cfarm_rsa.pub"
"hostname" : "bigboard"
"user" : "hiro"
"src-location" : "/home/hiro/Work/metaverse/src"
"build-location" : "/home/hiro/Work/metaverse/build"
"build-flags" : "-j8"

This will allow cfarm to setup a git remote for your project which will
be the same as the name of the .cdep. This remote will be used to push code
to the machines.

To allow cfarm to build your project you need to specify the build directory,
and the user we use to log in. If your ssh key isn't part of the authorized
users, we use the ssh-key to try and access the machine. Once we are on
the machine will call cmake --build -- $build-flags to build the version
we just pushed.

##Commands##
cfarm understands two concepts building and testing
both of the commands can be used with a per machine target or all machines target

cfarm build all
cfarm build Machine A

cfarm test all
cfarm test Machine C Machine B


##Technology##
  http://www.pygit2.org/
  http://libgit2.github.com/
  https://gist.github.com/jkubicek/410050
