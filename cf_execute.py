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

from __future__ import with_statement

from functools import wraps
import inspect
import sys
import textwrap

#must come before any fabric api
import cf_fabric_patches

from fabric import state
from fabric.utils import abort, warn, error
from fabric.network import to_dict, normalize_to_string, disconnect_all
from fabric.context_managers import settings
from fabric.job_queue import JobQueue
from fabric.task_utils import crawl, merge, parse_kwargs
from fabric.exceptions import NetworkError
from fabric.api import env


#this is a override for the fabric _execute method which allows us
#to have multiple connections to the same host. We want this to happen
#since a person can have multiple workers on the same host

import fabric.tasks

original_fabric_execute_impl = fabric.tasks._execute

def execute(task, *args, **kwargs):
    if 'workers' in kwargs:
        #monkey patch to use my _execute
        fabric.tasks._execute = _execute
        with settings(dedupe_hosts=False):
            fabric.tasks.execute(task,*args,**kwargs)
        #restore the original _execute
        fabric.tasks._execute = original_fabric_execute_impl
    else:
        fabric.tasks.execute(task,*args,**kwargs)


#this is a quick and dirty patch
def _execute(task, host, my_env, args, kwargs, jobs, queue, multiprocessing):
    """
    Primary single-host work body of execute()
    """
    # Log to stdout
    if state.output.running and not hasattr(task, 'return_value'):
        print("[%s] Executing task '%s'" % (host, my_env['command']))
    # Create per-run env with connection settings
    local_env = to_dict(host)
    local_env.update(my_env)
    # Set a few more env flags for parallelism
    if queue is not None:
        local_env.update({'parallel': True, 'linewise': True})
    # Handle parallel execution
    if queue is not None: # Since queue is only set for parallel
        name = local_env['host_string']
        workers = kwargs['workers']
        worker = workers[name]

        # Wrap in another callable that:
        # * expands the env it's given to ensure parallel, linewise, etc are
        #   all set correctly and explicitly. Such changes are naturally
        #   insulted from the parent process.
        # * nukes the connection cache to prevent shared-access problems
        # * knows how to send the tasks' return value back over a Queue
        # * captures exceptions raised by the task
        def inner(args, kwargs, queue, name, worker, env):
            #setup the correct host_string for this process
            #since the env currently has the worker cfarm name as the
            #host_string which is always the actual connection_name
            env['host_string'] = worker.connection_name
            state.env.update(env)

            def submit(result):
                queue.put({'name': name, 'result': result})
            try:
                key = normalize_to_string(state.env.host_string)
                state.connections.pop(key, "")

                #copy kwargs and remove workers and replace it
                #with the current worker this only works since we control
                #the tasks we are calling
                my_kwargs = kwargs
                my_kwargs.pop('workers')
                my_kwargs['worker']=worker

                submit(task.run(*args, **kwargs))
            except BaseException, e: # We really do want to capture everything
                # SystemExit implies use of abort(), which prints its own
                # traceback, host info etc -- so we don't want to double up
                # on that. For everything else, though, we need to make
                # clear what host encountered the exception that will
                # print.
                if e.__class__ is not SystemExit:
                    sys.stderr.write("!!! Parallel execution exception under host %r:\n" % name)
                    submit(e)
                # Here, anything -- unexpected exceptions, or abort()
                # driven SystemExits -- will bubble up and terminate the
                # child process.
                raise

        # Stuff into Process wrapper
        kwarg_dict = {
            'args': args,
            'kwargs': kwargs,
            'queue': queue,
            'name': name,
            'worker' : worker,
            'env': local_env,
        }
        p = multiprocessing.Process(target=inner, kwargs=kwarg_dict)
        # Name/id is host string
        p.name = name
        # Add to queue
        jobs.append(p)
    # Handle serial execution
    else:
        with settings(**local_env):
            return task.run(*args, **kwargs)
