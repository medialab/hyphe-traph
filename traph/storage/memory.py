# =============================================================================
# Memory Storage Class
# =============================================================================
#
# Class storing the data in a byte array.
#

# TODO: this does not work currently and must be partially rewritten!


# Main class
class MemoryStorage(object):

    def __init__(self, block_size):

        # Properties
        self.block_size = block_size
        self.array = bytearray()
        self.size = 0

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
            block = self.size
            self.size += self.block_size
        else:
            self.array[block:block + self.block_size] = data

        return block
