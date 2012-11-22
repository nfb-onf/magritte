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

        # format requirements in pip format (name==version)
        requirements = []
        for requirement in self.requirements:
            requirements.append(requirement.replace('-', '=='))
        requirements_file = open(self.package_cache.requirements_pip_filename, "w")
        requirements_file.write("\n".join(requirements))
        requirements_file.close()

        # format requirements in tgz format (name-version.tgz)
        requirements = []
        for requirement in self.requirements:
            requirements.append('%s.tgz' % requirement)
        requirements_file = open(self.package_cache.requirements_tgz_filename, "w")
        requirements_file.write("\n".join(requirements))
        requirements_file.close()

    def save_requirements_to_local_dists_dir(self):
        for requirement in self.requirements:
            dists_dir = self.package_cache.dists_dir
            versions_dir = self.package_cache.versions_dir
            dist_file = '%s/%s.tgz' % (dists_dir, requirement)
            command = 'tar -zcf %s %s' % (dist_file, requirement)
            args = shlex.split(command)
            logger.info("creating dist:%s", dist_file)
            p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=versions_dir)
            stdoutdata, stderrdata = p.communicate()
            if stdoutdata: logger.info(stdoutdata)
            if stderrdata: logger.error(stderrdata)

    def push_requirements_to_pypi_server(self, server):
        for requirement in self.requirements:
            versions_dir = self.package_cache.versions_dir
            version_dir = "%s/%s" % (versions_dir, requirement)
            command = 'python setup.py register -r %s sdist upload -r %s' % (server, server)
            args = shlex.split(command)
            p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=version_dir)
            stdoutdata, stderrdata = p.communicate()
            if stdoutdata: logger.info(stdoutdata)
            if stderrdata: logger.error(stderrdata)
