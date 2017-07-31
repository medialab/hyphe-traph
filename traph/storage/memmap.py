# =============================================================================
# Memory Map Storage Class
# =============================================================================
#
# Class abstracting reading the given file using python's mmap module
#
import mmap


# Main class
class MemMapStorage(object):

    def __init__(self, block_size, file):

        # Properties
        self.block_size = block_size
        self.file = file
        self.map = mmap.mmap(file.fileno(), access=mmap.ACCESS_READ, length=0)

    # Method reading a block in the map and returning the contained node
    def read(self, block):
        return self.map[block:block + self.block_size] or None

    # Method releasing the map from memory
    def release(self):
        self.map.close()
