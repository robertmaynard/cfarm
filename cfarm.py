#!/bin/env python

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

#import our helper functions
import cf_git as git
import cf_cmake as cmake
import cf_worker as worker
import cf_farm as farm

from fabric.api import env as fabric_env


#given a path figure out which project we are in, this is
#done by using git and cmakecache.txt parsing
def find_farm(path):
  #get our cwd
  root_path = git.get_project_root(path)
  if not root_path:
    root_path = cmake.get_project_root(path)
  return root_path

#init a farm of workers
def init_farm(working_dir):
  #setup that we use ssh settings
  fabric_env.use_ssh_config = True

  #find the where .cfarm is located
  farm_root = find_farm(working_dir)

  #parse the .cfarm directory that relates to the git repo we are located in
  # if no .cfarm, list short help, refer to github readme
  #build the collection of workers and set the initial state of each worker
  return farm.Farm(farm_root)

#init a single worker
def farm_worker_setup(name):
  #take the worker from the farm that matches the name passed in
  # if no worker found, send nice error stating so
  #
  # ssh into the user machine
  #create a bare git directory in the source directory
  #setup a post-receive hook to set the working directory
  #to be equal to the
  pass

#make a single work build
def farm_worker_build(name):
  pass

#make a single work test
def farm_worker_test(name):
  pass

if __name__ == '__main__':
  #load up the farm, todo allow command options to set where the source dir is
  #todo we need command option parse to figure out what functions to call
  farm = init_farm( "." )
  print 'farm source dir: ', farm.source()

  worker_name = "metaverse"
  worker = farm.worker(worker_name)

  git.remotes(farm.source())
  git.remote_exists(farm.source(),'github')










