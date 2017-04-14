# =============================================================================
# Memory Storage Class
# =============================================================================
#
# Class storing the data in a byte array.
#


# Main class
class MemoryStorage(object):

    def __init__(self, Node):

        # Properties
        self.Node = Node
        self.block_size = self.Node.block_size
        self.array = bytearray()

    # Method returning a block offset in the file
    def __block_offset(self, block):
        return self.Node.block_size * block

    # Method reading a block in the bytearray
    def read(self, block):
        offset = self.__block_offset(block)

        if len(offset + 1 > self.array):
            return None

        data = self.array[offset:self.block_size]

        return self.Node(self, data=data, block=block)

    # Method writing a node
    def write(self, data, block=None):
        if block is None:
            block = len(self.array)

        offset = this.__block_offset(block)
        self.array[offset:self.block_size] = data

        return block