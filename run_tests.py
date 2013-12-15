#!/bin/env python

import cfarm

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
for w in workers:
  print w.hostname
  print w.user
  print w.src_location
  print w.build_location
  print w.build_flags

