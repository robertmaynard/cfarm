#!/bin/env python

import cfarm

from fabric.api import env as fabric_env
fabric_env.use_ssh_config = True

class FakeRepo:
  def __init__(self,fake_path):
    self.path = fake_path


#verify that we can do a simple test
path = cfarm.cmake.get_project_root( "./tests/cmake_cache" )
print path == "/Users/robert/Work/Dax/src"

#well this only works on my machine
repo = cfarm.git.Repo(path)
print repo.remote_exists('github')
print repo.remote_exists('origin')

farm2 = cfarm.farm.Farm(FakeRepo("./tests/basic_read"))

worker_names = farm2.worker_names()
print worker_names
print 'metaverse' in worker_names
print 'bigboard' in worker_names

workers = farm2.workers()

remote_worker = [w for w in workers if w.name == 'local']
if len(remote_worker) == 1:
  remote_worker = remote_worker[0]

  #verify that we can create a bare repo
  #this is serial code
  remote_repo = cfarm.git.RemoteRepo(remote_worker)
  remote_repo.create_bare()
  remote_repo.install_hooks()

  #now we should add the remote repo to our local repo






