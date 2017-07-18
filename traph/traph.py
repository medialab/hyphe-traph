# =============================================================================
# Traph Class
# =============================================================================
#
# Main class representing the Traph data structure.
#
import re
from collections import defaultdict
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

        # Webentity creation rules are stored in RAM
        self.default_webentity_creation_rule = re.compile(
            default_webentity_creation_rule,
            re.I
        )

        self.webentity_creation_rules = {}

        for prefix, pattern in webentity_creation_rules.items():
            self.add_webentity_creation_rule(prefix, pattern, create)


    # =========================================================================
    # Internal methods
    # =========================================================================
    def __generate_web_entities_ids(self, number):
        header = self.lru_trie.header
        last_webentity_id = header.last_webentity_id()
        header.increment_last_webentity_id_by(number)
        header.write()

        return range(last_webentity_id + 1, last_webentity_id + number + 1)

    def __add_prefixes(self, prefixes):
        webentity_ids = self.__generate_web_entities_ids(len(prefixes))

        for i in range(len(prefixes)):
            prefix = prefixes[i]
            webentity_id = webentity_ids[i]

            node, history = self.lru_trie.add_lru(prefix)
            node.set_webentity(webentity_id)
            node.write()

    def __apply_webentity_creation_rule(self, rule_prefix, lru):

        regexp = self.webentity_creation_rules[rule_prefix]
        match = regexp.search(lru)

        if not match:
            return False

        prefix = match.group()
        expanded_prefixes = self.expand_prefix(prefix)

        if len(expanded_prefixes):
            self.__add_prefixes(expanded_prefixes)

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
    def index_batch_crawl(self, data):
        # data is supposed to be a JSON of this form:
        # {pages:{'lru':'<lru>', 'lrulinks':[<lrulink1>, ...]}}
        #
        # TODO: return a JSON containing created entities:
        # {stats:{}, webentities:{'<weid>':[<prefix1>, ...]}}
        pass

    def add_webentity_creation_rule(self, prefix, pattern, write_in_trie=True):
        print 'add webentity ' + prefix + ' - ' + str(write_in_trie)
        print self.webentity_creation_rules
        self.webentity_creation_rules[prefix] = re.compile(
            pattern,
            re.I
        )

        if write_in_trie:
            node, history = self.lru_trie.add_lru(prefix)
            node.flag_as_webentity_creation_rule()
            node.write()
        # TODO: if write_in_trie, depth first search to apply the rule (create entities)

    def remove_webentity_creation_rule(self, prefix):
        # TODO
        pass

    def create_webentity(self, prefixes, expand=False):
        # TODO
        # Return an error if one of the prefixes is already attributed to a we
        pass

    def delete_webentity(self, weid, weid_prefixes):
        # TODO
        # Note: weid is not strictly necessary, but it helps to check
        #       data consistency
        pass

    def add_webentity_prefix(self, weid, prefix):
        # TODO
        pass

    def remove_webentity_prefix(self, weid, prefix):
        # TODO
        pass

    def retrieve_prefix(self, lru):
        # TODO: return the first webentity prefix above lru
        # Raise an error in lru not in trie
        # Worst case scenario should be default we creation rule:
        # raise an error if no prefix found
        pass

    def retrieve_webentity(self, lru):
        # TODO: return the first webentity id above lru
        # Raise an error in lru not in trie
        # Worst case scenario should be default we creation rule:
        # raise an error if no webentity id found
        pass

    def 

    def expand_prefix(self, prefix):
        # TODO: expand
        return [prefix]

    def add_page(self, lru):
        node, history = self.lru_trie.add_page(lru)

        # FIXME: expected behavior is:
        #        1) Retrieve all creation rules triggered 'above' in the trie
        #        2) Apply them in order to get CANDIDATE prefixes
        #        3) Two cases:
        #           3a) All prefixes are smaller OR EQUAL (upper) than an existing prefix
        #               -> Nothing happens (webentity already exists)
        #           3b) A prefix is STRICTLY longer (lower) than existing prefixes
        #               -> apply the longest prefix as a new webentity

        # Here we need to deal with webentity creation rules
        for rule_prefix in history.rules_to_apply():
            if self.__apply_webentity_creation_rule(rule_prefix, lru):
                return node

        self.__apply_webentity_default_creation_rule(lru)
        return node

    def add_links(self, links):
        store = self.link_store

        # TODO: this will need to return created web entities
        inlinks = defaultdict(list)
        outlinks = defaultdict(list)
        pages = dict()

        for source_page, target_page in links:

            # Adding pages
            if not source_page in pages:
                node = self.add_page(source_page)
                pages[source_page] = node
            if not target_page in pages:
                node = self.add_page(target_page)
                pages[target_page] = node

            # Handling multimaps
            outlinks[source_page].append(target_page)
            inlinks[target_page].append(source_page)

        for source_page, target_pages in outlinks.items():
            source_node = pages[source_page]
            target_blocks = (pages[target_page].block for target_page in target_pages)

            store.add_outlinks(source_node, target_blocks)

        for target_page, source_pages in inlinks.items():
            target_node = pages[target_page]
            source_blocks = (pages[source_page].block for source_page in source_pages)

            store.add_inlinks(target_node, source_blocks)

    def close(self):

        # Cleanup
        self.lru_trie_file.close()
        self.link_store_file.close()

    def clear(self):
        # TODO
        pass

    # =========================================================================
    # Iteration methods
    # =========================================================================
    def links_iter(self, out=True):
        for page_node, lru in self.lru_trie.pages_iter():
            if not page_node.has_outlinks():
                continue

            for link_node in self.link_store.link_nodes_iter(page_node.outlinks()):
                yield lru, self.lru_trie.windup_lru(link_node.target())
