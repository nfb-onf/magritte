
import os, tempfile
import shlex, subprocess, shutil
import re
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from package_cache import PackageCache


class Getter(object):

    def __init__(self):
        self.package_cache = PackageCache()
        self.utils = self.package_cache.utils

        try:
            self.package_cache.init_downloaded_packages()
        except Exception as e:
            logger.info("caught %s when reading downloaded_packages_json_file", e)

    def list_tmp_pip_build_dirs(self):
        tmp_pip_build_dirs = []
        tmpdir = tempfile.gettempdir()
        for subdir in os.listdir(tmpdir):
            if re.match("^pip-.*-build$", subdir):
                tmp_pip_build_dirs.append("%s/%s" % (tmpdir, subdir))
        for subdir in os.listdir(self.package_cache.dumps_dir):
            tmp_pip_build_dirs.append("%s/%s" % (self.package_cache.dumps_dir, subdir))
        return tmp_pip_build_dirs


    def clean_pip_build_dirs(self):
        for tmp_pip_build_dir in self.list_tmp_pip_build_dirs():
            shutil.rmtree(tmp_pip_build_dir)


    def get_packages_from_lists_of_urls(self, url_files):
        all_downloaded_packages = []
        urls = self.get_urls_from_filenames(url_files)
        for url in urls:
            logger.info("Getting package %s ...", url)
            self.clean_pip_build_dirs()
            success = False
            args = shlex.split('pip install --no-install --force-reinstall --ignore-installed --upgrade "%s" -b "%s"' % (url, self.package_cache.dumps_dir))
            p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=open(os.devnull))
            stdout = p.stdout.readlines()
            downloaded_names = None
            for line in stdout:
                match = re.match("^Successfully downloaded (.*)", line)
                if match:
                    downloaded_names = match.groups()[0].split(' ')
                else:
                    continue
                success = True
                break
            if not success:
                logger.info('Error when downloading %s : %s', url, ''.join(stdout))
                self.package_cache.skipped_packages.append(url)
                continue

            if downloaded_names:
                downloaded_packages = self.find_downloaded_packages(downloaded_names)
                if downloaded_packages and downloaded_packages not in all_downloaded_packages:
                    all_downloaded_packages.append(downloaded_packages)

        self.package_cache.create_downloaded_packages_json_file(all_downloaded_packages)

        if self.package_cache.skipped_packages:
            logger.error('%s = \n%s ', self.package_cache.skipped_packages_urls_filename, self.package_cache.skipped_packages)
            skipped_packages_file = open(self.package_cache.skipped_packages_urls_filename, 'w')
            skipped_packages_file.write(''.join(self.package_cache.skipped_packages)+'\n')
            skipped_packages_file.close()

        self.clean_pip_build_dirs()


    def find_downloaded_packages(self, downloaded_names):
        packages = {}
        for source_dir in self.list_tmp_pip_build_dirs():
            pkg_name = self.package_cache.get_pkg_name(source_dir)
            pkg_version = self.package_cache.get_pkg_version(source_dir)
            pkg_fullname = self.package_cache.get_pkg_fullname(source_dir)
            normalised_pkg_name = self.normalize_pkg_name(pkg_name)
            version_dir = '%s/%s' % (self.package_cache.versions_dir, pkg_fullname)
            if pkg_fullname and pkg_fullname not in os.listdir(self.package_cache.versions_dir):
                shutil.move(source_dir, version_dir)
            packages[normalised_pkg_name] = (pkg_name, pkg_version)
        package_name = self.normalize_pkg_name(downloaded_names[0])
        if package_name in packages:
            package = [packages[package_name]]
        else:
            self.package_cache.skipped_packages.append(package_name)
            return
        deps = []
        for dep in downloaded_names[1:]:
            logger.info("found dependency %s", dep)
            deps.append(packages[self.normalize_pkg_name(dep)])
        if deps:
            package.append(deps)
        return package

    def get_urls_from_filenames(self,filenames):
        urls_from_filenames=[]
        for filename in filenames:
            try:
                fileIN = open(filename, "r")
            except Exception as e:
                logger.error("Opening %s : %s", filename, e)
                continue
            for url in fileIN.readlines():
                url = url.strip()
                if not url:
                    continue
                if url.startswith('#'):
                    continue
                urls_from_filenames.append(url)
        return urls_from_filenames


    def normalize_pkg_name(self, name):
        return name.lower().replace('-','_')

    def list_downloaded_versions(self):
        print "Downloaded packages :"
        for version_dir in os.listdir(self.package_cache.versions_dir):
            print version_dir
        print

    def list_skipped_packages(self):
        print "Skipped packages :"
        print open(self.package_cache.skipped_packages_urls_filename).read()
        print


