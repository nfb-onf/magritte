import os
import shlex, subprocess
import utils

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
        self.requirements = collector.get_requirements()

    def save_requirements_to_local_dists_dir(self):
        dists_dir = self.package_cache.dists_dir
        versions_dir = self.package_cache.versions_dir
        requirements = []
        for (req_name, req_version) in self.requirements:
            req_file_name = '%s-%s.tgz' % (req_name, req_version)
            req_package = "%s-%s" % (req_name, req_version)
            requirements.append(req_file_name)
            utils.Utils().make_dir("%s/%s" % (dists_dir, req_name))
            dist_file = '%s/%s/%s' % (dists_dir, req_name, req_file_name)
            command = 'tar -zcf %s %s' % (dist_file, req_package)
            args = shlex.split(command)
            logger.info("creating dist:%s", dist_file)
            p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=versions_dir)
            stdoutdata, stderrdata = p.communicate()
            if stdoutdata: logger.info(stdoutdata)
            if stderrdata: logger.error(stderrdata)
        # requirements in tgz format (name==version)
        requirements_file = open(self.package_cache.requirements_tgz_filename, "w")
        requirements_file.write("\n".join(requirements))
        requirements_file.close()
        logger.info('packages were saved in %s', dists_dir)
        logger.info('requirement file: %s', self.package_cache.requirements_tgz_filename)


    def push_requirements_to_pypi_server(self, server):
        versions_dir = self.package_cache.versions_dir
        requirements = []
        for (req_name, req_version) in self.requirements:
            req_package = "%s-%s" % (req_name, req_version)
            req_spec = "%s==%s" % (req_name, req_version)
            requirements.append(req_spec)
            version_dir = "%s/%s" % (versions_dir, req_package)
            command = 'python setup.py register -r %s sdist upload -r %s' % (server, server)
            args = shlex.split(command)
            p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=version_dir)
            stdoutdata, stderrdata = p.communicate()
            if stdoutdata: logger.info(stdoutdata)
            if stderrdata: logger.error(stderrdata)
        # requirements in pip format (name==version)
        requirements_file = open(self.package_cache.requirements_pip_filename, "w")
        requirements_file.write("\n".join(requirements))
        requirements_file.close()
        logger.info('packages were pushed to %s', server)
        logger.info('requirement file: %s', self.package_cache.requirements_pip_filename)
