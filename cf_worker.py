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

class Worker:

  def __init__(self, path):
    self.__read_worker(path)

    #workers name is not the host name! but the name of the file
    #that way we can have multiple workers per host
    self.name,ext = os.path.splitext(os.path.basename(path))


  def __read_worker(self,path):
    f = open(path,'r')
    j = json.load(f)

    #now assign the properties in the json file as member variables of
    #the class
    for key in j:
      self.__dict__[ key ] = j[key]


    print dir(self)