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

import os
import os.path

from fabric.api import env as fabric_env
from fabric.api import run as fabric_run
from fabric.api import open_shell as fabric_shell
from fabric.api import prompt as fabric_prompt
from fabric.context_managers import cd as fabric_rcd
from fabric.context_managers import settings as fabric_settings
from fabric.tasks import execute as fabric_execute
from fabric.context_managers import hide,show

import cf_worker
import cf_git


class Farm:
  def __init__(self, repo):

    #setup that we use ssh settings
    fabric_env.use_ssh_config = True

    self.__git_repo = repo
    self.__source_dir = os.path.join(repo.path,'.cfarm')

    self.__workers = {}

    self.__read_workers()

  def workers(self):
    return self.__workers

  def worker_names(self):
    return self.__workers.keys()

  def repo(self):
    return self.__git_repo

  def source_dir(self):
    return self.__source_dir

  #Returns if the setup worked or not
  def setup(self,worker_names):
    for worker_name in worker_names:
      #take the worker from the farm that matches the name passed in
      # if no worker found, send nice error stating so
      if worker_name not in self.__workers:
        print 'no worker found with that name'
        continue

      print 'setting up worker: ', worker_name
      worker = self.__workers[worker_name]
      #
      #create a bare git directory under the source directory
      #setup a post-receive hook to set the working directory
      #to be equal to the source directory
      worker_repo = cf_git.RemoteRepo(worker)
      worker_repo.create_bare()
      worker_repo.install_hooks()
      #
      #now we have to add the worker as a git remote
      #remote url looks like username@host:path/to/repository.git
      #
      worker_host_name = worker.connection_name
      worker_path = worker_repo.git_location #need the git repo not src dir

      #construct the full remote url
      remote_url = worker_host_name + ":" + worker_path

      #first remove the remote in case it already exists and we need
      #to change the url, and than add it
      self.repo().add_remote(worker_name,remote_url)

      #push current head as a starting point
      self.repo().push(worker_name,'+HEAD:refs/heads/master')

      #now get cfarm to remote into the build
      #directory and run ccmake
      fabric_execute(self.__configure, worker, host=worker_host_name)
    return True

  def __configure(self, worker):
    #make directory first
    with fabric_settings(warn_only=True):
      command = "mkdir " +  worker.build_location
      fabric_run(command)

    #run ccmake if the user wants
    run_configure = fabric_prompt('Would you like to run ccmake: ', default='y', validate=r'^(y|n)$')
    if(run_configure == 'y'):
      command = "ccmake -G " + worker.build_generator + " " + worker.src_location
      with fabric_rcd(worker.build_location):
        fabric_run(command)


  def build(self, worker_names):
    workers = self.push(worker_names)
    if workers:
      #if we have multiple workers that use the same host,
      #that host will build each of those workers sequentially
      host_list = [w.connection_name for w in workers]
      with fabric_settings(parallel=True):
        fabric_execute(self.__build, workers, hosts=host_list)
      return True
    return False

  def __build(self, workers):
    my_host_name = fabric_env.host

    valid_workers = [w for w in workers if w.hostname == my_host_name]
    for w in valid_workers:
      print 'building on worker:', w.name
      with fabric_rcd(w.build_location):
        #don't make a failed build a reason to abort
        with fabric_settings(warn_only=True):
          #build up build command
          command = "cmake --build ."
          #add in build flags if we have any
          if(w.build_flags != None):
            command += " -- " + w.build_flags
          fabric_run(command)


  def test(self, worker_names):
    workers = self.push(worker_names)
    if workers:
      #if we have multiple workers that use the same host,
      #that host will test each of those workers sequentially
      host_list = [w.connection_name for w in workers]
      with fabric_settings(parallel=True):
        fabric_execute(self.__test, workers, hosts=host_list)
      return True
    return False

  def __test(self, workers):
    my_host_name = fabric_env.host

    #better only be 1
    valid_workers = [w for w in workers if w.hostname == my_host_name]
    for w in valid_workers:
      print 'testing on worker:', w.name
      with fabric_rcd(w.build_location):
        with fabric_settings(warn_only=True):
          fabric_run("ctest")

  def push(self, worker_names):
    #get the valid subset of workers from worker_names
    workers = [self.__workers[w] for w in self.__workers if self.__workers[w].name in worker_names ]

    if len(workers) == 0:
      print 'no worker found with that name'
      return None

    for w in workers:
      self.repo().push(w.name,'+HEAD:refs/heads/master')
    return workers


  def __read_workers(self):
    def valid_ext(file):
      return file.endswith(".cdep")

    def full_path(file):
      return os.path.join(self.__source_dir,file)

    def make_worker(path):
      return cf_worker.Worker(path)

    for root, dirs, files in os.walk(self.__source_dir):
      dirs = []
      valid_files = filter(valid_ext, files)
      full_paths = map(full_path, valid_files)
      workers = map(make_worker, full_paths)

      self.__workers = {}
      for w in workers:
        self.__workers[w.name]=w

