Magritte
========

Magritte is a command with options to fetch python packages from a list of pip urls,
including their dependencies, save them to a local cache or upload them to a pypi server.

## Usage: magritte
(without options it displays this help)

## Options:
-h or --help : display this help
-r or --reset : delete all created files and directories from local cache (in ~/.magritte/)
-d or --download <package url> : fetch one package only (will also fetch dependent packages)
-g or --get <lists of files> : fetch packages listed from text files, in "pip urls" format
-s or --save : build requirement file and save packages as tgz archives in ~/.magritte/dists/
-p or --push <server>: build requirement file and push packages to a specified pypi server (defined in ~/.pypirc)
--list : list downloaded packages versions
--skipped : list packages that were skipped because of errors
--verbose: display more messages

Options can be combined, except the get and save (or push) options;
the workflow is to reset, get, get again if required, then save (or push).

## Content Organization:
Created files and directories are under ~/.magritte:
dump/ : temp dir for downloaded source directories
versions/ : collection of all downloaded source directories
dists/ : collection of saved distribution packages in tgz format
downloaded_packages.json : list of downloaded packages with their dependencies
requirements-in-pip-format.txt : list of versioned packages to use with a local pypi server
requirements-in-tgz-format.txt : list of versioned packages to use with a local http server
skipped-packages.txt :  list of skipped packages; the get command can use it to retry downloading

## Dependencies:
The magritte command relies on the presence of a ~/.pypirc file defining the uploading server.
(See: http://docs.python.org/2/distutils/packageindex.html)

## About the local dists directory:
The ~/.magritte/dists/ directory can be served with any http server, or used as a local file repository
It is not emptied with the reset command, so obsolete or unused packages must be removed manually.

## To do:
- [ ] Improve documentation
