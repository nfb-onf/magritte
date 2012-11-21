#!/usr/bin/env python
"""
Magritte is a command with options to fetch python packages  from a list of pip urls,
including their dependencies, and upload them to a local pypi server.

Usage:
magritte
(without options is displays this help)

Options:
-h or --help : display this help
-r or --reset : delete all created files and directories
-g or --get <lists of files with pip urls> : fetch packages listed in text files
-p or --push <server>: build requirement file and push packages to a specified pypi server
-l or --list : list downloaded packages versions
-s or --skipped : list packages that were skipped because of errors
-v or --verbose: display more messages

Options can be combined, except the get and push options;
the workflow is to reset, get, get again if required, then push.

Created files and directories are under ~/.magritte:
dump/ : temp dir for downloaded source directories
versions/ : collection of all downloaded source directories
downloaded_packages.json : list of downloaded packages with their dependencies
requirements.txt : list of versioned packages in order of dependency (to use in your project)
skipped-packages.txt :  list of skipped packages; the get command can use it to retry downloading
"""

import sys, getopt
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from magritte.getter import Getter
from magritte.pusher import Pusher

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def main():
    try:
        try:
            opts, args = getopt.getopt(sys.argv[1:], "hrgplsv",
                ["help", "reset", "get", "push", "list", "skipped", "verbose"])
        except getopt.error, msg:
            raise Usage(msg)

    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        sys.exit(2)

    if not opts:
        print __doc__
        sys.exit(0)
    verbose = False
    get = False
    push = False
    list_downloaded = False
    skipped = False
    reset = False


    for o, a in opts:
        if o in ("-h", "--help"):
            print __doc__
            sys.exit(0)

        # process arguments
        if o in ("-v", "--verbose"):
            verbose = True
        if o in ("-r", "--reset"):
            reset = True
        if o in ("-g", "--get"):
            get = True
        if o in ("-p", "--push"):
            push = True
        if o in ("-l", "--list"):
            list_downloaded = True
        if o in ("-s", "--skipped"):
            skipped = True

    if verbose:
        logger.setLevel(logging.INFO)
    if push and get:
        logger.error("Can't get and push at the same time; get, then push...")
        sys.exit(2)

    if reset or get or list or skipped or push:
        getter = Getter()
        if reset:
            getter.package_cache.reset()
        if get:
            getter.get_packages_from_lists_of_urls(args)
        if list_downloaded:
            getter.list_downloaded_versions()
        if skipped:
            getter.list_skipped_packages()
        if push:
            if not args:
                logger.error("Push requires a pypi server argument")
                sys.exit(2)
            pusher = Pusher(getter.package_cache)
            pusher.build_requirements()
            server = args[0]
            pusher.push_requirements_to_pypi_server(server)

    sys.exit(0)
