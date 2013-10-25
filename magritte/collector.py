#!/usr/bin/env python
"""expects data from stdin in json format"""
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from collections import OrderedDict

class ConflictingVersionError(Exception):
    pass

class RequiredAttributeMissingError(Exception):
    pass

class ImpossibleVersionComparisonException(Exception):
    pass

class Collector(object):
    def __init__(self):
        self.collection = OrderedDict()

    def get_other_versions(self, package_name, package_version):
        other_versions = []
        for other_package_name, other_package_version in self.collection.iterkeys():
            if other_package_name == package_name\
            and not other_package_version == package_version:
                other_versions.append((other_package_name, other_package_version))
        return other_versions

    def append_to_packages_list(self, package_name, package_version):
        other_versions =  dict(self.get_other_versions(package_name, package_version)).values()
        if other_versions:
            lowest = min(other_versions + [package_version])
            highest = max(other_versions + [package_version])
            if highest < lowest:
                raise ImpossibleVersionComparisonException("version %s of %s cannot be higher than %s" % (lowest, package_name, highest))
            if package_version < highest:
                logger.warning("downgrading %s from version %s to version %s",package_name, highest, package_version)
                del self.collection[(package_name, highest)]
            elif package_version > lowest:
                logger.warning("version %s of %s is higher than %s, ignored",package_version, package_name, lowest)
                return
        self.collection[package_name, package_version] = package_name, package_version


    def collect_dependencies(self, package_dependencies):
        for dependency in package_dependencies:
            package_name = dependency[0]
            package_version = dependency[1]
            self.append_to_packages_list(package_name, package_version)


    def traverse_dependencies(self, package):
        package_name = package[0][0]
        package_version = package[0][1]
        if not package_name:
            raise RequiredAttributeMissingError("package %s requires a name" % package)
        if not package_version:
            raise RequiredAttributeMissingError("package %s requires a version" % package)
        package_dependencies = None
        if len(package) == 2:
            package_dependencies = package[1]
        if package_dependencies:
            self.collect_dependencies(package_dependencies)
        self.append_to_packages_list(package_name, package_version)

    def traverse(self, structure):
        for package in structure:
            self.traverse_dependencies(package)

    def format_requirements(self):
        requirements = []
        for name,version in self.collection.iterkeys():
            requirements.append("%s-%s" % (name, version))
        return requirements

    def get_requirements(self):
        requirements = []
        for name, version in self.collection.iterkeys():
            requirements.append((name, version))
        return requirements

if __name__ == '__main__':
    from sys import stdin, stdout
    import simplejson
    structure = simplejson.load(stdin)
    collector = Collector()
    collector.traverse(structure)
    stdout.write("\n".join(collector.format_requirements()))

