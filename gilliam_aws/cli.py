# Copyright 2013 Johan Rydberg.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import os
import sys
import textwrap
import logging

from gilliam_client.config import (StageConfig, FormationConfig)
from gilliam_client import util

from . import commands


class Config(object):

    def __init__(self, project_dir, stage_config, stage):
        self.project_dir = project_dir
        self.stage_config = stage_config
        self.stage = stage

_DEBUG_FORMAT = '%(name)s [%(levelname)s]: %(message)s'
_NORMAL_FORMAT = '%(message)s'


def main():
    """Main entry point for the command-line tool."""
    parser = argparse.ArgumentParser(
        prog='gilliam-aws',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('-D', '--debug', action='store_true')
    parser.add_argument('-s', '--stage',
                        metavar='STAGE', dest='stage')
    parser.add_argument('-q', '--quiet', dest='quiet',
                        action='store_true', default=False)
    cmds = dict(_init_commands(parser))

    options = parser.parse_args()
    logging.basicConfig(
        stream=sys.stdout,
        level=(logging.DEBUG if options.debug else
               logging.INFO if options.verbose else
               logging.WARNING),
        format=_DEBUG_FORMAT if options.debug else _NORMAL_FORMAT)

    project_dir = util.find_rootdir()

    form_config = (
        FormationConfig.make(project_dir) if project_dir else
        None)
    options.stage = (
        options.stage if options.stage else
        form_config.stage if form_config else
        None)


    try:
        stage_config = (
            StageConfig.make(options.stage) if options.stage else
            None)
    except EnvironmentError as err:
        sys.exit("%s: %s: cannot read stage config: %s" % (
                options.cmd, options.stage, err))

    config = Config(project_dir, stage_config, options.stage)
                         
    cmd = cmds[options.cmd]
    cmd.handle(config, options)

    
def _init_commands(parser):
    """Initialize the commands."""
    subparsers = parser.add_subparsers(title='subcommands', dest='cmd')
    for name, cls in commands.load():
        cmd = cls(subparsers.add_parser(
                name, help=cls.synopsis,
                description=textwrap.dedent(cls.__doc__),
                formatter_class=argparse.RawDescriptionHelpFormatter))
        yield name, cmd
