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
from fabric.context_managers import hide,show

import cf_worker
import cf_git
import cf_execute


class Farm(object):
  def __init__(self, repo):

    #setup that we use ssh settings
    fabric_env.use_ssh_config = True
    fabric_env.forward_agent = True

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
  def setup(self,worker_names, user_setup_args):
    if len(user_setup_args) > 0:
      print 'unable to support user defined args for setup currently'
      return

    for worker_name in worker_names:
      #take the worker from the farm that matches the name passed in
      # if no worker found, send nice error stating so
      if worker_name not in self.__workers:
        print 'no worker found with that name'
        continue

      print 'setting up worker: ', worker_name
      worker = self.__workers[worker_name]
      #
      #create a git directory under the source directory
      #setup a post-receive hook to set the working directory
      #to be equal to the source directory
      worker_repo = cf_git.RemoteRepo(worker)
      worker_repo.create()
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
      cf_execute.execute(self.__setup, worker = worker, host=worker_host_name)
    return True

  def build(self, worker_names, user_build_args):
    user_args = " ".join(user_build_args)
    workers = self.push(worker_names)

    if workers == None:
      return False

    host_list = [name for name in workers]
    is_parallel = len(host_list) > 1

    if(is_parallel):
      #fabric by default treats hosts as unique, and if you have multiple jobs
      #that use the same hostname they are all passed to that fabric worker.
      #what we do is inject our own fabric_execut that pulls in more env
      #settings to create a 2 way mapping from worker names to fabric connections
      with fabric_settings(parallel=True):
        cf_execute.execute(self.__build, hosts=host_list, workers=workers, user_args=user_args)
    else:
      w = workers[host_list[0]]
      cf_execute.execute(self.__build, hosts=w.connection_name, worker=w, user_args=user_args)
    return True

  def test(self, worker_names, user_test_args):
    user_args = " ".join(user_test_args)

    workers = self.push(worker_names)
    if workers == None:
      return False

    host_list = [name for name in workers]
    is_parallel = len(host_list) > 1

    if(is_parallel):
      #fabric by default treats hosts as unique, and if you have multiple jobs
      #that use the same hostname they are all passed to that fabric worker.
      #what we do is inject our own fabric_execut that pulls in more env
      #settings to create a 2 way mapping from worker names to fabric connections
      with fabric_settings(parallel=True):
        cf_execute.execute(self.__test, hosts=host_list, workers=workers, user_args=user_args)
    else:
      w = workers[host_list[0]]
      cf_execute.execute(self.__test, hosts=w.connection_name, worker=w, user_args=user_args)
    return True

  def __setup(self, worker):
    #make directory first
    with fabric_settings(warn_only=True):
      command = "mkdir -p " +  worker.build_location
      fabric_run(command)

    #run ccmake / cmake depending on user input
    run_configure = fabric_prompt('Would you like to run ccmake: ', default='y', validate=r'^(y|n)$')
    command = worker.generateSetupCommand(is_interactive=(run_configure=='y'))
    with fabric_rcd(worker.build_location):
      fabric_run(command)

  def __build(self, worker, user_args):
    my_host_name = fabric_env.host

    print 'building on worker:', worker.name

    with fabric_rcd(worker.build_location):
      #don't make a failed build a reason to abort
      with fabric_settings(warn_only=True):
        command = worker.generateBuildCommand(user_args)
        fabric_run(command)

  def __test(self, worker, user_args):
    my_host_name = fabric_env.host

    print 'testing on worker:', worker.name

    with fabric_rcd(worker.build_location):
      with fabric_settings(warn_only=True):
        command = worker.generateTestCommand(user_args)
        fabric_run(command)


  def push(self, worker_names):
    #get the valid subset of workers from worker_names
    workers = {k: self.__workers[k] for k in self.__workers if k in worker_names}

    if len(workers) == 0:
      print 'no worker found with that name'
      return None

    for name in workers:
      self.repo().push(name,'+HEAD:refs/heads/master')
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

