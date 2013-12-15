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

import cf_worker

class Farm:
  def __init__(self, repo):
    self.__git_repo = repo
    self.__source_dir = os.path.join(repo.path,'.cfarm')

    self.__read_workers()

  def workers(self):
    return self.__workers

  def worker_names(self):
    return [worker.name for worker in self.__workers]

  def repo(self):
    return self.__git_repo

  def source_dir(self):
    return self.__source_dir

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
      self.__workers = map(make_worker, full_paths)
