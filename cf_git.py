
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

#must come before any fabric api
import cf_fabric_patches

from fabric.api import local as fabric_local
from fabric.api import run as fabric_remote

from fabric.contrib.files import upload_template as fabric_template
from fabric.tasks import execute as fabric_execute

from fabric.context_managers import lcd as fabric_lcd
from fabric.context_managers import cd as fabric_rcd
from fabric.context_managers import settings as fabric_settings
from fabric.context_managers import hide,show

import inspect
import os.path



#construct a local repo, where path is the path to git repo
class Repo(object):
  def __init__(self, path):

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
        result = self.git_call("rev-parse","--show-toplevel")
    #string path will have newline sep, so strip them
    if result.failed:
      return None
    return result.rstrip('\n\r')


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
    if self.remote_exists(remote_name):
      self.git_call("remote", "rm", remote_name)
    self.git_call("remote", "add", remote_name, remote_url)


  #setup the remote so that we push the lfs data to the
  #lfs server not the worker. This is pretty much needed
  #as you cant push lfs data to a machine that isn't running
  #lfs-server
  def add_lfs_endpoint(self, remote_name, lfs_dict):
    if lfs_dict:
        key = "remote." + remote_name + ".lfsurl"
        url = lfs_dict['push_url']
        self.git_call("config", key, url)

  #return a list of all the remote repos that a git project has
  def remotes(self):
    remotes = self.git_call("remote")
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
  def push(self, remote_name, ref ):
    #include porcelain so we can get parse-able output
    return self.git_call("push", "--porcelain", remote_name, ref )


  #helper function to call git commands
  #dict arg cwd is used to set where we call git commands from
  def git_call(self, command, *args):
    comm_list = ["git",command]
    arg_list = [ item for item in args ]
    comm_list += arg_list

    invoke_command = " ".join(comm_list)

    #set the current working directory
    with self.cd(self.path):
        return self.run(invoke_command, capture=True)


#Designed for setting up a bare remote repos that checkouts code in
#the user defined src directory
class RemoteRepo(object):
  def __init__(self, cfWorker, lfs):
    self.connection_name = cfWorker.connection_name
    self.src_location = cfWorker.src_location
    self.git_location = os.path.join(self.src_location, '.git')
    self.lfs = lfs

    self.cd = fabric_rcd
    self.run = fabric_remote


  #creates a bare git repo at the current repos path
  def create(self):
    fabric_execute(self.__create, host=self.connection_name)

  def __create(self):
    #first make the directory
    with fabric_settings(warn_only=True):
      self.run("mkdir -p " +  self.src_location)

    #move into the directory and make it a git repo, and setup
    #the hooks we need
    with self.cd( self.src_location ):
      self.run("git init " + self.src_location)
    with self.cd( self.git_location ):
      self.run("git config --bool receive.denyCurrentBranch false")
      self.run("git config --path core.worktree " + self.src_location)
      if self.lfs:
        #to get lfs to run properly we need to add both a remote
        #and a lfs url, otherwise it wont work properly when we try
        #to fetch data. See https://github.com/git-lfs/git-lfs/issues/930
        with fabric_settings(warn_only=True):
          self.run("git remote rm lfs")

        self.run("git remote add lfs " + self.lfs['fetch_url'])
        #this needs to have info/lfs/ or else you get very weird 403
        #errors about cookies need to be enabled
        self.run("git config lfs.url " + self.lfs['fetch_url'] + "/info/lfs/")

  #install the hooks to automatically update the src-location of the worker
  #to the latest git commit
  def install_hooks(self):
    #find the location of the template file
    fabric_execute(self.__install_hooks, host=self.connection_name)

  def __install_hooks(self):
    #get the location of the template file based on our location
    this_file_loc = os.path.abspath(inspect.getfile(inspect.currentframe()))
    current_dir = os.path.dirname( this_file_loc )

    template_file = os.path.join(current_dir,'templates/post-receive')
    if self.lfs:
      template_file = os.path.join(current_dir,'templates/post-receive-with-lfs')


    #setup the destination of the hooks
    dest = os.path.join(self.git_location,'hooks/post-receive')

    #make sure the hooks directory exists
    with fabric_settings(warn_only=True):
      self.run("mkdir -p " +  os.path.join(self.git_location,'hooks'))

    #setup the template dictionary to create valid hooks
    context_dict = { }
    context_dict['src_location']=self.src_location

    #upload and create the hooks
    fabric_template(template_file, destination=dest, context=context_dict)

    #make the file executable
    ch_command = "chmod +x " + dest
    self.run(ch_command)


