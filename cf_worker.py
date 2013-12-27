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

class Worker(object):

  def __init__(self, path):
    self.__read_worker(path)

    #workers name is not the host name! but the name of the file
    #that way we can have multiple workers per host
    self.name,ext = os.path.splitext(os.path.basename(path))


  def __read_worker(self,path):
    f = open(path,'r')
    j = json.load(f)

    #give optional arguments default values
    self.build_flags = None
    self.env_setup = None

    #now assign the properties in the json file as member variables of
    #the class
    for key in j:
      self.__dict__[ key ] = j[key]

    #setup the connection name
    self.connection_name = self.user + "@" + self.hostname