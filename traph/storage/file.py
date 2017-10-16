# =============================================================================
# File Storage Class
# =============================================================================
#
# Class abstracting random access file handling for the Traph.
#
import os
from traph.storage.memmap import MemMapStorage


# Main class
class FileStorage(object):

    def __init__(self, block_size, file):

        # Properties
        self.block_size = block_size
        self.file = file

    def __len__(self):
        self.file.seek(0, os.SEEK_END)
        return self.file.tell()

    # Method returning the number of blocks
    def count_blocks(self):
        return self.__len__() / self.block_size

    # Method returning whether the file is corrupted
    def check_for_corruption(self):
        file_length = self.__len__()

        if file_length % self.block_size:
            return True

        return False

    # Method reading a block in the file and returning the contained node
    def read(self, block=None):

        if block is not None:
            self.file.seek(block)

        data = self.file.read(self.block_size)

        return data or None

    # Method writing a node
    def write(self, data, block=None):
        if block is not None:
            self.file.seek(block)
        else:
            self.file.seek(0, os.SEEK_END)

        self.file.write(data)

        # TODO: can be avoided if we do not append
        block = self.file.tell() - self.block_size

        return block

    # Method returning a map
    def map(self):
        return MemMapStorage(self.block_size, self.file)
