##Todo##

1. Implement two new options called 'build_env' and 'test_env'. These
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

2. We need a way to state Visual Studio Generators plus Config.
   How about something like this:

   ````
   {
    ...
    "build_generator" : "Visual Studio 10 Win64 Release"
    
   }
   ````   
   
   We can parse that to determine the proper config option to pass
   down to cmake --build.

   Trying to break the setup into OS,Generator,Version,Architecture,...
   seems to be pointless since the configure step is so abitrary that
   every machine will need special flags. Remember cfarm is aiming
   to only cover the standard use case, screw edge cases.


3. Automatically send modifications in the current git repo to the machines
   when invoking the build command. Will require us to run some pretty fancy
   git commands to package up the changes and push it without changing any git
   history on the client.

