# =============================================================================
# File Storage Class
# =============================================================================
#
# Class abstracting random access file handling for the Traph.
#
import os
from lru_trie_node import LRUTrieNode, LRU_TRIE_NODE_BLOCK_SIZE


# Function computing the offset for the given block in the LRU trie
def lru_trie_block_offset(block):
    return block * LRU_TRIE_NODE_BLOCK_SIZE


class FileStorage(object):

    def __init__(self, lru_trie_file):

        # Properties
        self.lru_trie_file = lru_trie_file
        self.lru_trie_file_cursor = 0

    def read_lru_trie_node(self, block):
        offset = lru_trie_block_offset(block)

        self.lru_trie_file.seek(offset)

        binary_data = self.lru_trie_file.read(LRU_TRIE_NODE_BLOCK_SIZE)

        if not binary_data:
            return None

        return LRUTrieNode(binary_data=binary_data, block=block)

    def create_lru_trie_node(self, char):
        return LRUTrieNode(char)

    def write_lru_trie_node(self, node):
        if node.block:
            offset = lru_trie_block_offset(block)
            self.lru_trie_file.seek(offset)
        else:
            self.lru_trie_file.seek(0, os.SEEK_END)

        self.lru_trie_file.write(node.pack())

        block = self.lru_trie_file.tell() / LRU_TRIE_NODE_BLOCK_SIZE
        node.block = block

        return block
