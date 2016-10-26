#=============================================================================
#
#  Copyright (c) Kitware, Inc.
#  All rights reserved.
#  See LICENSE.txt for details.
#
#  This software is distributed WITHOUT ANY WARRANTY; without even
#  the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#  PURPOSE.  See the above copyright notice for more information.
#
#=============================================================================

import os.path
import json

class Worker(object):

  def __init__(self, path):
    self.__read_worker(path)

    #workers name is not the host name! but the name of the file
    #that way we can have multiple workers per host
    self.name,ext = os.path.splitext(os.path.basename(path))

    #add support for a pretty name to the work
    self.pretty_name = self.name

  def generateSetupCommand(self, is_interactive):
    command = "cmake"
    if(is_interactive):
      command = "ccmake"

    if(self.build_generator):
      command += " -G '" + self.build_generator +"'"

    if(self.build_configuration):
      command += " -DCMAKE_BUILD_TYPE:STRING="+self.build_configuration

    if(self.cpp_compiler):
      command += " -DCMAKE_CXX_COMPILER:FILEPATH="+self.cpp_compiler

    if(self.c_compiler):
      command += " -DCMAKE_C_COMPILER:FILEPATH="+self.c_compiler

    if(self.cuda_compiler):
      command += " -DCMAKE_CUDA_COMPILER:FILEPATH="+self.cuda_compiler

    if(self.cuda_host_compiler):
      command += " -DCMAKE_CUDA_HOST_COMPILER:FILEPATH="+self.cuda_compiler

    if(self.c_flags):
      command += " -DCMAKE_C_FLAGS:STRING="+self.c_flags

    if(self.cpp_flags):
      command += " -DCMAKE_CXX_FLAGS:STRING="+self.cpp_flags

    if(self.cuda_flags):
      command += " -DCMAKE_CUDA_FLAGS:STRING="+self.cuda_flags

    if(self.library_type):
      #if somebody passes us not static or shared we disable the option
      lib_type="DBUILD_SHARED_LIBS_NOT_FOUND"
      if(self.library_type.lower() == "static"):
        lib_type="FALSE"
      elif(self.library_type.lower() == "shared"):
        lib_type="TRUE"
      command += " -DBUILD_SHARED_LIBS:BOOL="+lib_type

    return command + " " + self.src_location

  def generateBuildCommand(self, user_args):
    #add the build flags to the front of the tool args if they exist
    command = "cmake --build ."
    if self.build_configuration:
      #always pass the build configuration so that we handle mulit-config
      #generators
      command += " --config " + self.build_configuration
    if len(user_args) > 0:
      command += " " + user_args
    if self.build_flags != None:
      command += " -- " + self.build_flags
    return command

  def generateTestCommand(self, user_args):
    return "ctest " + user_args


  def __read_worker(self,path):
    f = open(path,'r')
    j = json.load(f)

    #give optional arguments default values of nothing
    self.build_flags = None
    self.build_configuration = None
    self.c_compiler = None
    self.cpp_compiler = None
    self.cuda_compiler = None
    self.cuda_host_compiler = None

    self.c_flags = None
    self.cpp_flags = None
    self.cuda_flags = None

    self.library_type = None

    #now assign the properties in the json file as member variables of
    #the class
    for key in j:
      self.__dict__[ key ] = j[key]

    #setup the connection name
    self.connection_name = self.user + "@" + self.hostname
