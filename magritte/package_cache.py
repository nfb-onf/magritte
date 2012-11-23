
import os
import simplejson
import shlex
import shutil
import re
import subprocess

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from utils import Utils


class PackageCache(object):

    def __init__(self):
        self.utils = Utils()

        cache_dir = "%s/.magritte" % os.path.expanduser('~')
        self.utils.make_dir(cache_dir)

        self.dumps_dir = "%s/dump" % cache_dir
        self.utils.make_dir(self.dumps_dir)

        self.versions_dir = "%s/versions" % cache_dir
        self.utils.make_dir(self.versions_dir)

        self.dists_dir = "%s/dists" % cache_dir
        self.utils.make_dir(self.dists_dir)

        self.downloaded_packages_json_filename = "%s/%s" % (cache_dir, 'downloaded_packages.json')
        self.skipped_packages_urls_filename = "%s/%s" % (cache_dir, 'skipped-packages.txt')
        self.requirements_pip_filename = "%s/%s" % (cache_dir, 'requirements-in-pip-format.txt')
        self.requirements_tgz_filename = "%s/%s" % (cache_dir, 'requirements-in-tgz-format.txt')
        self.skipped_packages = []
        self.all_downloaded_packages = []

    def init_downloaded_packages(self):
        if self.utils.file_exists(self.downloaded_packages_json_filename):
            self.downloaded_packages_json_file = open(self.downloaded_packages_json_filename, "r")
            all_downloaded_packages_json = self.downloaded_packages_json_file.read()
            self.all_downloaded_packages = simplejson.loads(all_downloaded_packages_json)
            self.downloaded_packages_json_file.close()

    def get_info_from_setup(self, source_dir, option ):
        args = shlex.split('python setup.py --%s' % option)
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=open(os.devnull), cwd=source_dir)
        return p.stdout.readlines().pop().strip()

    def get_pkg_requires(self, source_dir):
        return self.get_info_from_setup(source_dir, 'requires' )

    def get_package_infos(self, source_dir):
        infos = {}
        try:
            pkginfo_file = open("%s/PKG-INFO" % source_dir, "r")
            pkginfos = pkginfo_file.readlines()
            pkginfo_file.close()
            for info in pkginfos:
                match = re.match("(.*): (.*)", info.strip())
                if match:
                    infos[match.groups()[0]] = match.groups()[1]
        except:
            infos['Name'] = self.get_info_from_setup(source_dir, 'name')
            infos['Version'] = self.get_info_from_setup(source_dir, 'version')
        return infos

    def get_pkg_name(self, source_dir):
        return self.get_package_infos(source_dir).get('Name')

    def get_pkg_version(self, source_dir):
        return self.get_package_infos(source_dir).get('Version')

    def get_pkg_fullname(self, source_dir):
        infos = self.get_package_infos(source_dir)
        return "%(Name)s-%(Version)s" % infos

    def reset(self):
        """reset working session by deleting all created files and directories"""
        self.all_downloaded_packages = []
        self.clean_versions_dir()
        self.delete_result_files()
        logger.info('Reset completed')

    def clean_versions_dir(self):
        for version_dir in os.listdir(self.versions_dir):
            shutil.rmtree("%s/%s" % (self.versions_dir, version_dir))

    def delete_result_files(self):
        self.utils.delete_file(self.downloaded_packages_json_filename)
        self.utils.delete_file(self.skipped_packages_urls_filename)
        self.utils.delete_file(self.requirements_pip_filename)
        self.utils.delete_file(self.requirements_tgz_filename)

    def create_downloaded_packages_json_file(self, all_downloaded_packages):
        downloaded_packages_json = simplejson.dumps(all_downloaded_packages, indent='  ')
        self.downloaded_packages_json_file = open(self.downloaded_packages_json_filename, 'w')
        self.downloaded_packages_json_file.write(downloaded_packages_json)
        self.downloaded_packages_json_file.close()
