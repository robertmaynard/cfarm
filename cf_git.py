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


from fabric.api import local as fabric_local
from fabric.api import run as fabric_remote
from fabric.context_managers import lcd as fabric_lcd
from fabric.context_managers import cd as fabric_rcd
from fabric.context_managers import settings as fabric_settings
from fabric.context_managers import hide,show



#construct a local or remote repo, where
#path is the path to git repo ( or where you want to create it ).
class Repo:
  def __init__(self, path, remote=False):
    if(remote):
      self.cd = fabric_rcd
      self.run = fabric_remote
    else:
      self.cd = fabric_lcd
      self.run = fabric_local

    self.path = path #setup path for project_root
    self.path = self.root() #find the proper root of the repo


  #given a path find the git root directory for that path
  def root(self):
    #we don't know if the path is a valid git repo so we don't want
    #fabric to fail if we aren't, so tell it to only warn.
    with fabric_settings(warn_only=True):
      with hide('warnings', 'status', 'running', 'stdout', 'stderr'):
        string_path = self.__git_call("rev-parse","--show-toplevel")
    #string path will have newline sep, so strip them
    if len(string_path)==0:
      return None
    return string_path.rstrip('\n\r')


  #
  #
  #  Remote functions
  #
  #
  #

  #add a git remote to a git a local repo
  #remote_name is the name for this git remote
  #remote_url is the url for the new remote
  def add_remote(self, remote_name, remote_url):
    self.__git_call("remote", "add", remote_name, remote_url)

  #return a list of all the remote repos that a git project has
  def remotes(self):
    remotes = self.__git_call("remote")
    return remotes.split()

  def remote_exists(self, remote):
    return remote in self.remotes()

  #
  #
  #  Push Functions
  #
  #
  #

  #push a local branch to a remote
  #ref is the branch name,SHA1, or other ref we want to push
  #remote_name is the remote we are pushing the branch to
  def push(self, ref, remote_name):
    #include porcelain so we can get parse-able output
    return self.__git_call("push", "--porcelain", remote_name, ref )


  #
  #
  # Init functions to create new git repos
  #
  #
  #
  #creates a bare git repo at the current repos path
  def create_bare(self):
    return self.__git_call("init","--bare")

  #helper function to call git commands
  #dict arg cwd is used to set where we call git commands from
  def __git_call(self, command, *args):
    comm_list = ["git",command]
    arg_list = [ item for item in args ]
    comm_list += arg_list

    invoke_command = " ".join(comm_list)

    #set the current working directory
    with self.cd(self.path):
        return self.run(invoke_command, capture=True)
