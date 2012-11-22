#!/usr/bin/env python
"""
Magritte is a command with options to fetch python packages from a list of pip urls,
including their dependencies, and upload them to a pypi server.

Usage: magritte
(without options it displays this help)

Options:
-h or --help : display this help
-r or --reset : delete all created files and directories from local cache (in ~/.magritte/)
-g or --get <lists of files> : fetch packages listed from text files, in "pip urls" format
-p or --push <server>: build requirement file and push packages to a specified pypi server (defined in ~/.pypirc)
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

Dependencies:
The magritte command relies on the presence of a ~/.pypirc file defining the uploading server.
(See: http://docs.python.org/2/distutils/packageindex.html)
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
            opts, args = getopt.getopt(sys.argv[1:], "hrgsp",
                ["help", "reset", "get", "save", "push", "list", "skipped", "verbose"])
        except getopt.error, msg:
            raise Usage(msg)

    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        sys.exit(2)

    if not opts:
        print __doc__
        sys.exit(0)

    verbose =  get = save = push = list_downloaded = skipped = reset = False

    for o, a in opts:
        if o in ("-h", "--help"):
            print __doc__
            sys.exit(0)

        # process arguments
        if o in ("-r", "--reset"):
            reset = True
        if o in ("-g", "--get"):
            get = True
        if o in ("-s", "--save"):
            save = True
        if o in ("-p", "--push"):
            push = True
        if o in ("--list",):
            list_downloaded = True
        if o in ("--skipped",):
            skipped = True
        if o in ("--verbose",):
            verbose = True

    if verbose:
        logger.setLevel(logging.INFO)

    # validate combination of options

    if get and (save or push):
        if save:
            logger.error("Can't get and save at the same time; get, then save...")
        if push:
            logger.error("Can't get and push at the same time; get, then push...")
        sys.exit(2)

    getter = Getter()

    if reset or get or list or skipped :
        if reset:
            getter.package_cache.reset()
        if get:
            getter.get_packages_from_lists_of_urls(args)
        if list_downloaded:
            getter.list_downloaded_versions()
        if skipped:
            getter.list_skipped_packages()

    if save or push:
        pusher = Pusher(getter.package_cache)
        pusher.build_requirements()

        if save:
            pusher.save_requirements_to_local_dists_dir()

        if push:
            if not args:
                logger.error("Push requires a pypi server argument")
                sys.exit(2)
            server = args[0]
            pusher.push_requirements_to_pypi_server(server)

    sys.exit(0)
