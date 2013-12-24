##Todo##

1. Implement env_setup and be able to source a user provided file
   before calling configure, build, and test. We might need to setup
   three options called:

   configure_env
   build_env
   test_env

2. Properly setup a windows worker and finish documenting how this is
   done by using a configure and build env file


3. setup a linux worker that exports a X display when running tests.


4. Investigate setting up template files for the configure, build, and test
   env.

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

   For a windows machine that needs to setup visual studio we need
   more options, so maybe we offer some basic templating support?

   ````
   {
    ...
    "build_generator" : "Ninja",
    "build_flags" : "-j8"
    "configure_env" : ["template": "WindowsMSVC", "version": "11"]
    "build_env" : ["template": "WindowsMSVC", "version" : "11"]
   }
   ````

   We than need to specify a location where we are going to place
   the templated files on the remote machine. Maybe hide them somewhere
   in the source dir, such as .cworker_env/*?

5. Teach the build command about --config so that window visual studio workers
   can be told which config to use. Maybe also think about adding a working
   setting called build_config which will be the default

9. Automatically send modifications in the current git repo to the machines
   when invoking the build command. Will require us to run some pretty fancy
   git commands to package up the changes and push it without changing any git
   history on the client.

