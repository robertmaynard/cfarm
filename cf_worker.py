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

    #now assign the properties in the json file as member variables of
    #the class
    for key in j:
      self.__dict__[ key ] = j[key]

    #setup the connection name
    self.connection_name = self.user + "@" + self.hostname
