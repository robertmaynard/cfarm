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

import json
import os.path

class Farm:
  def __init__(self, sdir):
    self.__source_dir = sdir

    #read the .cfarm directory parsing each file
    #with json creating a collection of workers

  def worker(self, wname):
    return None

  def source(self):
    return self.__source_dir
