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

import sys
import fnmatch

#import our helper functions
import cf_git as git
import cf_cmake as cmake
import cf_worker as worker
import cf_farm as farm

def short_usage( all_worker_names ):
  print 'CFarm growing C++ builds\n' + \
  'usage cfarm.py [setup machine] [build machine(s)] [test] machine(s)]\n'+\
  '\n'+\
  'Examples:' + \
  '\n'+\
  '  cfarm setup deliverator\n'+\
  '  cfarm build deliverator\n'+\
  '  cfarm test bigboard metaverse\n'

  if all_worker_names != None:
    print 'Current workers:'
    for w in all_worker_names:
      print ' -',w

def long_usage( ):
  short_usage( None )
  print 'To use cfarm you need a setup a configuration per project. This is \n' + \
  'done by creating a .cfarm folder in the root of your git repo that \n' + \
  'you want cfarm to work on (Yes cfarm only supports git, I said cfarm \n' + \
  'has no features). \n' + \
  ' \n' + \
  'The folder will look something like: \n' + \
  ' \n' + \
  '.cfarm/ \n' + \
    '  - metaverse.cdep \n' + \
    '  - deliverator.cdep \n' + \
    '  - bigboard.cdep \n' + \
  ' \n' + \
  ' \n' + \
  'Each .cdep file will describe how to deploy the project to a machine. This \n' + \
  'entails the following. Each file name is the cfarm workers name, allowing \n' + \
  'you to have multiple workers that point to the same host name. \n' + \
  ' \n' + \
  '{ \n' + \
  '  "hostname" : "bigboard", \n' + \
  '  "user" : "hiro", \n' + \
  '  "src_location" : "/home/hiro/Work/bigboard/src", \n' + \
  '  "build_location" : "/home/hiro/Work/bigboard/build", \n' + \
  '  "build_generator" : "Ninja", \n' + \
  '  "build_flags" : "-j8" \n' + \
  '} \n'

#given a path figure out which project we are in, this is
#done by using git and cmakecache.txt parsing
def find_git_repo(path):
  #get our cwd
  repo = git.Repo(path)
  if not repo.path:
    root_path = cmake.get_project_root(path)
    if root_path == None:
      long_usage()
      print 'no git repo found'
      exit(2)
    repo = git.Repo(root_path)
  return repo

#init a farm of workers
def init_farm(working_dir):

  #find the where .cfarm is located
  repo = find_git_repo(working_dir)

  #parse the .cfarm directory that relates to the git repo we are located in
  # if no .cfarm, list short help, refer to github readme
  #build the collection of workers and set the initial state of each worker
  f = farm.Farm(repo)
  if len(f.workers()) == 0:
    long_usage()
    print 'no workers found, I think you are missing a .cdep folder'
    exit(2)
  return f

def main(argv):
  farm = init_farm(".")

  #setup arg function table
  commands = {
    'configure':farm.setup, #i am lazy and keep using cmake terminology
    'setup':farm.setup,
    'build':farm.build,
    'test':farm.test
    }

  all_worker_names = farm.worker_names()

  #at this point we have a valid farm
  #verify arg length, be helpful and list current workers
  if len(argv) == 0:
    short_usage( all_worker_names  )
    sys.exit(2)

  #extract all worker names from the list, and extract everything
  #after -- to be arguments to pass to the function call
  wnames = []
  args = []

  try:
    arg_index = argv.index('--')
  except Exception, e:
    wnames = argv[1:]
  else:
    wnames = argv[1:arg_index]
    if len(argv) > arg_index+1:
      args = argv[arg_index+1:]

  #now check for the magic all name, and handle worker unix style globbing
  if 'all' in wnames:
    #support all by looking for it first and replacing
    #the rest of the argv with just all known worker names
    wnames = all_worker_names
  else:
    #check each worker name to see if it is a unix style globbing
    all_matching = []
    for pattern in wnames:
      matching = fnmatch.filter(all_worker_names,pattern)
      all_matching += matching
    unique = set(all_matching)
    wnames = list(unique)

  #call the correct function with the updated worker names
  if argv[0] in commands:
    commands[argv[0]]( wnames, args )
  elif argv[0] == 'help':
    short_usage( all_worker_names )
  else:
    short_usage( all_worker_names )
    sys.exit(2)

if __name__ == '__main__':
  main(sys.argv[1:])
