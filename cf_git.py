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


################################################################################
# HELPER GIT METHODS FOR CFARM
################################################################################
from fabric.api import local as fabric_local
from fabric.context_managers import lcd as fabric_lcd
from fabric.context_managers import settings as fabric_settings
from fabric.context_managers import hide,show

#helper function to call git commands
#dict arg cwd is used to set where we call git commands from
def git_call(command, *args, **kwargs):
  _cwd = kwargs.pop('cwd',None)

  comm_list = ["git",command]
  arg_list = [ item for item in args ]
  comm_list += arg_list

  invoke_command = " ".join(comm_list)


  #have this set by verbosity level
  with hide('warnings', 'status', 'running', 'stdout', 'stderr'):
    #set the current working directory
    if(_cwd):
      with fabric_lcd(_cwd):
        #call fabric_local with capturing turned on so we can parse commands
        return fabric_local(invoke_command, capture=True)
    else:
      return fabric_local(invoke_command, capture=True)

#
#
#  Root Dir
#
#
#

#given a path find the git root directory for that path
def get_project_root(path):
  #we don't know if the path is a valid git repo so we don't want
  #fabric to fail if we aren't, so tell it to only warn.
  with fabric_settings(warn_only=True):
    string_path = git_call("rev-parse","--show-toplevel", cwd=path)
  #string path will have newline sep, so strip them
  if 'fatal: Not a git repository ' in string_path:
    return None
  return string_path.rstrip('\n\r')


#
#
# Init functions to create new git repos
#
#
#
#creates a bare git repo at the given location
def create_bare(path):
  return git_call("init","--bare",cwd=path)


#
#
#  Remote functions
#
#
#

#add a git remote to a git a local repo
#remote_name is the name for this git remote
#remote_url is the url for the new remote
#local_git_repo is the directory that the local git repo to add to is in
def add_remote(remote_name, remote_url, local_git_repo):
  git_call("remote", "add", remote_name, remote_url, cwd=local_git_repo)

#return a list of all the remote repos that a git project has
def remotes(local_git_repo):
  remotes = git_call("remote", cwd=local_git_repo)
  return remotes.split()

def remote_exists(local_git_repo, remote):
  return remote in remotes(local_git_repo)

#
#
#  Push Functions
#
#
#

#push a local branch to a remote
#ref is the branch name,SHA1, or other ref we want to push
#remote_name is the remote we are pushing the branch to
def push(local_git_repo, ref, remote_name):
  #include porcelain so we can get parse-able output
  return git_call("push", "--porcelain", remote_name, ref )

if __name__ == '__main__':
  pass