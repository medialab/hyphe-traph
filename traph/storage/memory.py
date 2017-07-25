# =============================================================================
# Memory Storage Class
# =============================================================================
#
# Class storing the data in a byte array.
#


# Main class
class MemoryStorage(object):

    def __init__(self, block_size):

        # Properties
        self.block_size = block_size
        self.array = bytearray()

    def __len__(self):
        return len(self.array)

    # Method returning the number of blocks
    def count_blocks(self):
        return self.__len__() / self.block_size

    # Method clearing the memory
    def clear(self):
        self.array = bytearray()

    # Method reading a block in the bytearray
    def read(self, block):
        try:
            return self.array[block:block + self.block_size] or None
        except IndexError:
            return None
        except:
            raise

    # Method writing nodes to the bytearray
    def write(self, data, block=None):
        if block is None:
            self.array.extend(data)

            # TODO: cache the length maybe?
            block = len(self.array) - self.block_size
        else:
            self.array[block:block + self.block_size] = data

        return block
