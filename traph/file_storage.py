# =============================================================================
# File Storage Class
# =============================================================================
#
# Class abstracting random access file handling for the Traph.
#
import os


# Main class
class FileStorage(object):

    def __init__(self, block_size, file):

        # Properties
        self.block_size = block_size
        self.file = file

    # Method returning a block offset in the file
    def __block_offset(self, block):
        return self.block_size * block

    # Method returning whether the file is corrupted
    def check_for_corruption(self):
        self.file.seek(0, os.SEEK_END)
        file_length = self.file.tell()

        if file_length % self.block_size:
            return True

        return False

    # Method reading a block in the file and returning the contained node
    def read(self, block):
        offset = self.__block_offset(block)

        self.file.seek(offset)

        data = self.file.read(self.block_size)

        if not data:
            return None

        return data

    # Method writing a node
    def write(self, data, block=None):
        if block is not None:
            offset = self.__block_offset(block)
            self.file.seek(offset)
        else:
            self.file.seek(0, os.SEEK_END)

        self.file.write(data)

        block = (self.file.tell() - self.block_size) / self.block_size

        return block
