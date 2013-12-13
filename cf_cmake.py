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

#given a path find the git root directory for that path
def get_project_root(path):

  def words(fileobj):
    for line in fileobj:
        for word in line.split('='):
            yield word

  #see if we have a CMakeCache.txt file in our current location
  search_terms = ("CMAKE_HOME_DIRECTORY:INTERNAL")
  if os.path.exists(path):
    cmake_cache_file = os.path.join(path,"CMakeCache.txt")
    if os.path.isfile(cmake_cache_file):
      with open(cmake_cache_file) as cmake_cache:
        word_gen = words(cmake_cache)
        for item in word_gen:
          if item in search_terms:
            #get the path and strip trailing and leading whitespace!
            return word_gen.next().strip()

  return None
