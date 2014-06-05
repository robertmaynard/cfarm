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

from fabric.state import env
import fabric.utils
import fabric.io

#this is a override for the fabric puts method which allows us
#to use the pretty_name for a cfarm worker as the prefix for
#output

def puts(text, show_prefix=None, end="\n", flush=False):
    """
    An alias for ``print`` whose output is managed by Fabric's output controls.

    In other words, this function simply prints to ``sys.stdout``, but will
    hide its output if the ``user`` :doc:`output level
    </usage/output_controls>` is set to ``False``.

    If ``show_prefix=False``, `puts` will omit the leading ``[hostname]``
    which it tacks on by default. (It will also omit this prefix if
    ``env.host_string`` is empty.)

    Newlines may be disabled by setting ``end`` to the empty string (``''``).
    (This intentionally mirrors Python 3's ``print`` syntax.)

    You may force output flushing (e.g. to bypass output buffering) by setting
    ``flush=True``.

    .. versionadded:: 0.9.2
    .. seealso:: `~fabric.utils.fastprint`
    """
    from fabric.state import output, env
    if show_prefix is None:
        show_prefix = env.output_prefix
    if output.user:
        prefix = ""
        if env.pretty_host_string and show_prefix:
            prefix = "[%s] " % env.pretty_host_string
        elif env.host_string and show_prefix:
            prefix = "[%s] " % env.host_string
        sys.stdout.write(prefix + str(text) + end)
        if flush:
            sys.stdout.flush()

def output_loop(*args, **kwargs):
    ol = fabric.io.OutputLooper(*args, **kwargs)
    if env.has_key('pretty_host_string'):
        ol.prefix = "[%s] %s: " % (
                env.pretty_host_string,
                "out" if args[1] == 'recv' else "err"
            )
    else:
        ol.prefix = "[%s] %s: " % (
                env.host_string,
                "out" if args[1] == 'recv' else "err"
            )
    ol.loop()

fabric.utils.__dict__['puts'] = puts
fabric.io.__dict__['output_loop'] = output_loop


