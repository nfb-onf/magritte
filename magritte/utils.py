
import os

class Utils(object):

    def file_exists(self, filename):
        try:
            with open(filename) as f:
                f.close()
                return True
        except IOError as e:
            return False

    def delete_file(self, filename):
        if self.file_exists(filename):
            os.remove(filename)

    def make_dir(self, directory):
        if not os.path.exists(directory):
          os.mkdir(directory)
