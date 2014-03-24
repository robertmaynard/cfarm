##Todo##

1. Support toolchain files or -C configuration .cmake files on initial setup

2. Implement two new options called 'build_env' and 'test_env'. These
   are called using fabric.prefix before we run build and test

   build_env
   test_env

   A good test is showing how to setup a linux worker to export
   an X display for running test ( export :0.0 )

   What about setting up template files for the build, and test env.

   For a linux machine we would have the following:
   ````
   {
    ...
    "build_generator" : "Ninja",
    "build_flags" : "-j8"
    "test_env" : ['file': "/home/hiro/cfarm/ExportXDisplay"]
   }
   ````
   Which source a remote file.
3. Automatically send modifications in the current git repo to the machines
   when invoking the build command. Will require us to run some pretty fancy
   git commands to package up the changes and push it without changing any git
   history on the client.
4. Write a new protocol that makes windows support possible. I am thinking something
   the lines of a windows daemon or service that we can connect to and run
   remote commands from. ctest@home might have some resources we can leverage
   for this to work.

