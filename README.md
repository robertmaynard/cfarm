###CFarm###

CFarm goal is to keep numerous machines in sync when developing cross platform
C++ projects. You can think of a private continuous testing, without any fancy
reporting, user interface, or other 'features' that other tools have.


##Usage##

cfarm understands the commands: setup, build, and test. Each of these
commands be called with a specific deployment name(s), basic globing or the
keyword 'all'.

```
 cfarm setup all
 cfarm setup metaverse

 cfarm build all
 cfarm build deliverator
 cfarm build d* m*

 cfarm test all
 cfarm test bigboard metaverse
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

##Configuration##

To use cfarm you need a setup a configuration per project. This is
done by creating a .cfarm folder in the root of your git repo that
you want cfarm to work on (Yes cfarm only supports git).

The folder will look something like:
```
.cfarm/
  - metaverse.cdep
  - deliverator.cdep
  - bigboard.cdep
```

Each .cdep file will describe how to deploy the project with a set of
configuration(s). Each file name is the cfarm workers name, allowing
you to have multiple workers that point to the same physical machine.

Here is an example .cdep file with a single configuration:
```
{
"hostname" : "bigboard",
"user" : "hiro",
"compiler" : [ { "name" : "gcc", "cpp" : "/usr/bin/g++-4.6" } ]
"cpp_compiler" : "/usr/bin/g++-4.6",
"src_location" : "/home/hiro/Work/bigboard/src",
"build_location" : "/home/hiro/Work/bigboard/build",
"build_generator" : "Ninja",
"build_flags" : "-j8"
}
```

A deployment file can contain multiple configurations for a project by specify
multiple compilers, library types, and build configurations to use. This allows
you to setup a single deployment file to easily verify a project builds and tests
when using any number of compilers, or to verify a project builds with static
and shared libraries.

Here is an example .cdep file that specifies 3 compilers, and 2 library types,
which means the cfarm worker will build/test 6 versions of the project in parallel.
```
{
"hostname" : "bigboard",
"user" : "hiro",
"compiler" : [
   {"name" : "legacy_gcc",  "c" : "/usr/bin/gcc-4.6", "cpp" : "/usr/bin/g++-4.6"},
   {"name" : "gcc4.8",  "c" : "/usr/bin/gcc-4.8", "cpp" : "/usr/bin/g++-4.8"},
   {"name" : "clang",   "c" : "/usr/bin/clang",   "cpp" : "/usr/bin/clang++"}
   ],
"src_location" : "/home/hiro/Work/bigboard/src",
"build_location" : "/home/hiro/Work/bigboard/build",
"build_generator" : "Ninja",
"build_flags" : "-l8",
"build_configuration" : ["debug"]
"library_type" : [ "static", "shared" ]
}

###Required Settings###
Here is a list of required settings for a .cdep file:
- ```hostname```: Computer name, or ip address of worker.
- ```user```: User we are going to log in as.
- ```src_location```: Location to store the source for the current project.
- ```build_location```: Location to build the project.
- ```build_generator```: CMake generator to use for building.

###Optional Settings###
Here is a list of optional settings for a .cdep file:
- ```compiler```: Collection of C and/or C++ compiler to use.
- ```library_type```: If you want Statically and or Shared libraries.
- ```build_configuration```: Build configurations that you want to use such as: Debug, Release.
- ```build_flags```: List of flags for compilation, generally holds '-j<N>'


##Requirements##

```
Python 2.6 or 2.7
Fabric
```



