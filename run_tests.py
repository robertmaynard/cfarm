#!/bin/env python

import cfarm

from fabric.api import env as fabric_env
fabric_env.use_ssh_config = True

class FakeRepo:
  def __init__(self,fake_path):
    self.path = fake_path

class NoCheckRepo(cfarm.git.Repo):
  def __init__(self,path):
    self.cd = fabric_lcd
    self.run = fabric_local

    self.path = path #setup path for project_root

  def init(self):
    return self.__git_call("init")


#verify that we can do a simple test
path = cfarm.cmake.get_project_root( "./tests/cmake_cache" )
print path == "/Users/robert/Work/Dax/src"

#well this only works on my machine
repo = cfarm.git.Repo(path)
print repo.remote_exists('github')
print repo.remote_exists('origin')

#fake a real git repo to verify json reading works
farm2 = cfarm.farm.Farm(FakeRepo("./tests/basic_read"))

worker_names = farm2.worker_names()
print worker_names
print 'metaverse' in worker_names
print 'bigboard' in worker_names

workers = farm2.workers()

if('local' in workers):
  remote_worker = workers['local']

  #verify that we can create a bare repo
  #this is serial code
  remote_repo = cfarm.git.RemoteRepo(remote_worker)
  remote_repo.create_bare()
  remote_repo.install_hooks()

  #hook up a local repo to have that remote
  new_repo = NoCheckRepo("./tests/dummy_repo")
  new_repo.init()

  #need to construct a remote url
  new_repo.add_remote(remote_worker.name, remote_worker.git_url)




