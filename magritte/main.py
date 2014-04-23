#!/usr/bin/env python
"""
Magritte is a command with options to fetch python packages from a list of pip urls,
including their dependencies, save them to a local cache or upload them to a pypi server.

Usage: magritte
(without options it displays this help)

Options:
-h or --help : display this help
-r or --reset : delete all created files and directories from local cache (in ~/.magritte/)
-d or --download <package url> : fetch one package only (will also fetch dependent packages)
-g or --get <lists of files> : fetch packages listed from text files, in "pip urls" format
-s or --save : build requirement file and save packages as tgz archives in ~/.magritte/dists/
-p or --push <server>: build requirement file and push packages to a specified pypi server (defined in ~/.pypirc)
--list : list downloaded packages versions
--skipped : list packages that were skipped because of errors
--verbose: display more messages
--version: show version

Options can be combined, except the get and save (or push) options;
the workflow is to reset, get, get again if required, then save (or push).

Created files and directories are under ~/.magritte:
dump/ : temp dir for downloaded source directories
versions/ : collection of all downloaded source directories
dists/ : collection of saved distribution packages in tgz format
downloaded_packages.json : list of downloaded packages with their dependencies
requirements-in-pip-format.txt : list of versioned packages to use with a local pypi server
requirements-in-tgz-format.txt : list of versioned packages to use with a local http server
skipped-packages.txt :  list of skipped packages; the get command can use it to retry downloading

Dependencies:
The magritte command relies on the presence of a ~/.pypirc file defining the uploading server.
(See: http://docs.python.org/2/distutils/packageindex.html)

About the local dists directory:
The ~/.magritte/dists/ directory can be served with any http server, or used as a local file repository
It is not emptied with the reset command, so obsolete or unused packages must be removed manually.

"""

import sys, getopt
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import pkg_resources

from magritte.getter import Getter
from magritte.pusher import Pusher

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def version():
    return pkg_resources.get_distribution("magritte").version

def main():
    long_options = ["help", "reset", "download", "get", "save", "push", "list", "skipped", "verbose", "version"]
    short_options = 'hrdgsp'
    options_dict = dict()
    try:
        try:
            opts, args = getopt.getopt(sys.argv[1:], short_options, long_options)
        except getopt.error, msg:
            raise Usage(msg)

    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        sys.exit(2)

    if not opts:
        print "magritte %s" % version()
        print __doc__
        sys.exit(0)

    verbose = get = download = save = push = list_downloaded = skipped = reset = False

    for o, a in opts:
        if o in ("-h", "--help"):
            print __doc__
            sys.exit(0)

        # process arguments
        if o in ("-r", "--reset"):
            reset = True
        if o in ("-d", "--download"):
            download = True
        if o in ("-g", "--get"):
            get = True
        if o in ("-s", "--save"):
            save = True
        if o in ("-p", "--push"):
            push = True
        if o in ("-l", "--list",):
            list_downloaded = True
        if o in ("--skipped",):
            skipped = True
        if o in ("--verbose",):
            verbose = True
        if o in ("--version",):
            print version()

    if verbose:
        logger.setLevel(logging.INFO)

    # validate combination of options

    if (get or download) and (save or push):
        if save:
            logger.error("Can't get and save at the same time; get, then save...")
        if push:
            logger.error("Can't get and push at the same time; get, then push...")
        sys.exit(2)

    getter = Getter()

    if reset or download or get or list or skipped :
        if reset:
            getter.package_cache.reset()
        if download:
            getter.download_package_from_url(args)
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
