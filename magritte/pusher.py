import os
import shlex, subprocess

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from collector import Collector


class Pusher(object):
    def __init__(self, package_cache):
        self.package_cache = package_cache
        self.requirements = []

    def build_requirements(self):
        collector = Collector()
        collector.traverse(self.package_cache.all_downloaded_packages)
        self.requirements = collector.format_requirements()
        requirements_file = open(self.package_cache.requirements_filename, "w")
        requirements_file.write("\n".join(self.requirements))
        requirements_file.close()

    def push_requirements_to_pypi_server(self, server):
        for requirement in self.requirements:
            version_dir = "%s/%s" % (self.package_cache.versions_dir, requirement.replace('==', '-'))
            command = 'python setup.py register -r %s sdist upload -r %s' % (server, server)
            args = shlex.split(command)
            p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=open(os.devnull), cwd=version_dir)
            logger.info(''.join(p.stdout.readlines()))
