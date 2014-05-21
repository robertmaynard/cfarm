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
import itertools


def upgrade_compiler_property(json_dict):

  if not json_dict.has_key("c_compiler") and not json_dict.has_key("cpp_compiler"):
    return()

  #build up the json example to show how they can convert the deprecated
  #properties to the new properties
  compiler_list = {"name": "unkown" }

  if json_dict.has_key("c_compiler"):
    compiler_list["c"] = json_dict["c_compiler"]
    del json_dict["c_compiler"]

  if json_dict.has_key("cpp_compiler"):
    compiler_list["cpp"] = json_dict["cpp_compiler"]
    del json_dict["cpp_compiler"]

  json_dict["compiler"] = [compiler_list]



  compiler_setting_message = "\n".join(["The deployment properties 'c_compiler' and 'cpp_compiler' have been removed.",
                                        "Instead you should use the new 'compiler' property.",
                                        "Here is your .cdep file updated with the new 'compiler' property.",
                                        "" ]) #need a trailing \n
  compiler_setting_message +=  json.dumps(json_dict, sort_keys=True, indent=2, separators=(',', ': '))

  print compiler_setting_message

#What we need is individual workers, and worker matrix which map
#to a .cdep file. So we read a .cdep file and construct a worker collection
#we than fill the collection based on the matrix of options that are in that
#.cdep file
# this is reasonable since some of the properties of the .cdep file are
# constant across all elements in the matrix ( source tree, generator, build flags )
# We need to update cf_farm and cf_git to handle multiple build_locations
class WorkerMatrix(object):
  def __init__(self, path):
    #workers name is not the host name! but the name of the file
    #that way we can have multiple workers per host
    self.name,ext = os.path.splitext(os.path.basename(path))

    self.workers = []

    self.__read_deployment_file(path)
    self.__construct_matrix()

  def __read_deployment_file(self,path):
    f = open(path,'r')
    j = json.load(f)

    #give optional arguments default values of nothing
    self.build_flags = None
    self.build_configuration = None
    self.compiler = None
    self.library_type = None

    #warn about the deprecation of c_compiler and cpp_compiler setting,
    #Show the user what the cdep file would look like with the new setting
    #Should we ask the user if they want us to overwrite it?
    upgrade_compiler_property(j)

    #now assign the properties in the json file as member variables of
    #the class
    for key in j:
      self.__dict__[ key.lower() ] = j[key] #enforce all lower case variables

    #setup the connection name
    self.connection_name = self.user + "@" + self.hostname

  def __construct_matrix(self):

    def make_iter(item):
      if not item:
        return [None]
      elif hasattr(item, '__iter__'):
        return item
      else:
        return [item]

    #returns the compiler_name, if compiler_info is None we return None.
    #if compiler_info doesn't have the name key we make a name for it
    def make_compiler_name(compiler_info):
      if compiler_info:
        if not compiler_info.has_key("name"):
          if compiler_info.has_key("cpp"):
              compiler_info["name"] = os.path.basename(compiler_info["cpp"])
          elif compiler_info.has_key("c"):
              compiler_info["name"] = os.path.basename(compiler_info["c"])
          else:
              compiler_info["name"]="unkown"
        return compiler_info["name"]
      return None

    def make_build_subdir_name(compiler_name, config, lib_type):

      dir_name = []

      #make sure we have a compiler first
      if compiler_name:
        dir_name.append(compiler_name.lower())

      if config:
        dir_name.append(config.lower())

      if lib_type:
        dir_name.append(lib_type.lower())

      dir_name = "_".join(dir_name)
      return dir_name


    #need a way to easily construct a matrix of workers, The best way
    #looks to be using itertools.product

    compiler_types = make_iter(self.compiler)
    build_config = make_iter(self.build_configuration)
    lib_types = make_iter(self.library_type)

    worker_generator = itertools.product( compiler_types,
                                          build_config,
                                          lib_types)

    for worker_values in worker_generator:
      #transform our dictionary into a dictionary for the work
      #we do this by copying our dictonary and updating the
      #values for compiler, build_configuration, and library_type
      #to be one iteration of the product of all the combinations
      worker_dictonary = self.__dict__.copy()

      worker_dictonary["compiler"] = worker_values[0]
      worker_dictonary["build_configuration"] = worker_values[1]
      worker_dictonary["library_type"] = worker_values[2]

      #make sure the compiler dictionary has a name value, if it
      #doesn't make one based on the compiler info given to us
      #returns the compiler_name, if worker_dictonary doesn't have a compiler
      #section compiler_name is None
      compiler_name = make_compiler_name(worker_dictonary["compiler"])

      #generate a new build location for each worker,
      #this is a composite of the compiler name, library_type, and build_configuration
      dir_name = make_build_subdir_name(compiler_name, worker_values[1], worker_values[2])
      worker_dictonary["build_location"] = os.path.join(self.build_location,dir_name)

      self.workers.append( Worker(self.name, worker_dictonary) )


class Worker(object):

  def __init__(self, name, worker_state):

    self.name = name

    #dynamic create our member variables based on the dictionary coming
    #into us, we better be created by a WorkerMatrix class
    for key in worker_state:
      self.__dict__[ key ] = worker_state[key]

    #add support for a pretty name to the worker
    self.pretty_name = self.name + " (" + os.path.basename(self.build_location) + ") "

  def generateSetupCommand(self, is_interactive):
    command = "cmake"
    if(is_interactive):
      command = "ccmake"

    if(self.build_generator):
      command += " -G '" + self.build_generator +"'"

    if(self.build_configuration):
      command += " -DCMAKE_BUILD_TYPE:STRING="+self.build_configuration

    if(self.compiler.has_key("cpp")):
      command += " -DCMAKE_CXX_COMPILER:FILEPATH="+self.compiler["cpp"]

    if(self.compiler.has_key("c")):
      command += " -DCMAKE_C_COMPILER:FILEPATH="+self.compiler["c"]

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
