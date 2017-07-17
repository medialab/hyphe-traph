# =============================================================================
# Traph Class
# =============================================================================
#
# Main class representing the Traph data structure.
#
import re
from traph_batch import TraphBatch
from file_storage import FileStorage
from memory_storage import MemoryStorage
from lru_trie import LRUTrie
from lru_trie_walk_history import LRUTrieWalkHistory
from lru_trie_node import LRU_TRIE_NODE_BLOCK_SIZE
from link_store import LinkStore
from link_store_node import LINK_STORE_NODE_BLOCK_SIZE


# Main class
class Traph(object):

    # =========================================================================
    # Constructor
    # =========================================================================
    def __init__(self, create=False, folder=None,
                 default_webentity_creation_rule=None,
                 webentity_creation_rules=None):

        # TODO: solve path

        if create:
            # TODO: erase dir and all its content
            # TODO: make dir
            self.lru_trie_file = open(folder+'lru_trie.dat', 'wb+')
            self.link_store_file = open(folder+'link_store.dat', 'wb+')
        else:
            self.lru_trie_file = open(folder+'lru_trie.dat', 'rb+')
            self.link_store_file = open(folder+'link_store.dat', 'rb+')

        # Web entity creation rules are stored in RAM
        self.default_webentity_creation_rule = re.compile(
            default_webentity_creation_rule,
            re.I
        )

        self.webentity_creation_rules = {}

        for prefix, pattern in webentity_creation_rules.items():
            self.add_webentity_creation_rule(prefix, pattern, create)

        # LRU Trie initialization
        if folder:
            self.lru_trie_storage = FileStorage(
                LRU_TRIE_NODE_BLOCK_SIZE,
                self.lru_trie_file
            )
        else:
            self.lru_trie_storage = MemoryStorage(LRU_TRIE_NODE_BLOCK_SIZE)

        self.lru_trie = LRUTrie(self.lru_trie_storage)

        # Link Store initialization
        if folder:
            self.links_store_storage = FileStorage(
                LINK_STORE_NODE_BLOCK_SIZE,
                self.link_store_file
            )
        else:
            self.links_store_storage = MemoryStorage(
                LINK_STORE_NODE_BLOCK_SIZE)

        self.link_store = LinkStore(self.links_store_storage)

    # =========================================================================
    # Internal methods
    # =========================================================================
    def __add_prefixes(self, prefixes):
        for prefix in prefixes:

            # TODO: notify of webentity creation
            # TODO: 45 is a placeholder for the weid
            node, history = self.lru_trie.add_lru(prefix)
            node.set_webentity(45)
            node.write()

    def __apply_webentity_creation_rule(self, rule_prefix, lru):

        regexp = self.webentity_creation_rules[rule_prefix]
        match = regexp.search(lru)

        if not match:
            return False

        prefix = match.group()

        self.__add_prefixes(self.expand_prefix(prefix))

        return True

    def __apply_webentity_default_creation_rule(self, lru):

        regexp = self.default_webentity_creation_rule
        match = regexp.search(lru)

        if not match:
            return False

        prefix = match.group()

        self.__add_prefixes(self.expand_prefix(prefix))

        return True

    # =========================================================================
    # Public interface
    # =========================================================================
    def add_webentity_creation_rule(self, prefix, pattern, write_in_trie=True):
        self.webentity_creation_rules[prefix] = re.compile(
                pattern,
                re.I
            )

    def expand_prefix(self, prefix):
        # TODO: expand
        return [prefix]

    def batch(self):
        return TraphBatch(self)

    def add_page(self, lru):
        node, history = self.lru_trie.add_page(lru)

        # Here we need to deal with webentity creation rules
        for rule_prefix in history.rules_to_apply():
            if self.__apply_webentity_creation_rule(rule_prefix, lru):
                return node

        self.__apply_webentity_default_creation_rule(lru)
        return node

    def close(self):
        # Cleanup
        self.lru_trie_file.close()
        self.link_store_file.close()