# =============================================================================
# Traph Class
# =============================================================================
#
# Main class representing the Traph data structure.
#
import errno
import os
import re
from collections import defaultdict, Counter
from traph_write_report import TraphWriteReport
from storage import FileStorage, MemoryStorage
from lru_trie import LRUTrie, LRUTrieNode, LRU_TRIE_NODE_BLOCK_SIZE
from link_store import LinkStore, LINK_STORE_NODE_BLOCK_SIZE
from helpers import lru_variations


# Exceptions
class TraphException(Exception):
    pass


# Main class
class Traph(object):

    # =========================================================================
    # Constructor
    # =========================================================================
    def __init__(self, overwrite=False, folder=None, encoding='utf-8',
                 default_webentity_creation_rule=None,
                 webentity_creation_rules=None):

        # Handling encoding
        self.encoding = encoding

        create = overwrite

        # Solving paths
        if folder:
            lru_trie_path = os.path.join(folder, 'lru_trie.dat')
            link_store_path = os.path.join(folder, 'link_store.dat')

            # Ensuring the given folder exists
            try:
                os.makedirs(folder)
            except OSError as exception:
                if exception.errno == errno.EEXIST and os.path.isdir(folder):
                    pass
                else:
                    raise

            # Testing existence of files
            lru_trie_file_exists = os.path.isfile(lru_trie_path)
            link_store_file_exists = os.path.isfile(link_store_path)

            # Checking consistency
            if lru_trie_file_exists and not link_store_file_exists:
                raise TraphException(
                    'File inconsistency: `lru_trie.dat` file exists but not `link_store.dat`.'
                )

            if not lru_trie_file_exists and link_store_file_exists:
                raise TraphException(
                    'File inconsistency: `link_store.dat` file exists but not `lru_trie.dat`.'
                )

            # Do we need to create the files for the first time?
            create = overwrite or (not lru_trie_file_exists and not link_store_file_exists)

            flags = 'wb+' if create else 'rb+'

            self.lru_trie_file = open(lru_trie_path, flags)
            self.link_store_file = open(link_store_path, flags)

            self.lru_trie_storage = FileStorage(
                LRU_TRIE_NODE_BLOCK_SIZE,
                self.lru_trie_file
            )

            self.links_store_storage = FileStorage(
                LINK_STORE_NODE_BLOCK_SIZE,
                self.link_store_file
            )

            # Checking for corruption
            if self.lru_trie_storage.check_for_corruption():
                raise TraphException(
                    'File corrupted: `lru_trie.dat`'
                )

            if self.links_store_storage.check_for_corruption():
                raise TraphException(
                    'File corrupted: `link_store.dat`'
                )

        else:
            self.lru_trie_storage = MemoryStorage(LRU_TRIE_NODE_BLOCK_SIZE)
            self.links_store_storage = MemoryStorage(LINK_STORE_NODE_BLOCK_SIZE)

        # LRU Trie initialization
        self.lru_trie = LRUTrie(self.lru_trie_storage, encoding=encoding)

        # Link Store initialization
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
    def __encode(self, string):
        if isinstance(string, str):
            return string

        return string.encode(self.encoding)

    def __generated_web_entity_id(self):
        header = self.lru_trie.header
        header.increment_last_webentity_id()
        header.write()

        return header.last_webentity_id()

    def __add_prefixes(self, prefixes, use_best_case=True):
        # Check that prefixes are not already defining a web entity
        valid_prefixes_index = {}
        invalid_prefixes = []
        for prefix in prefixes:
            node, history = self.lru_trie.add_lru(prefix)

            if node.has_webentity():
                invalid_prefixes.append(prefix)
            else:
                valid_prefixes_index.update({prefix: [node, history]})

        if len(invalid_prefixes)>0 and not use_best_case:
            raise Exception('Some prefixes were already set: %s' % (invalid_prefixes))  # TODO: raise custom exception
            return

        elif len(invalid_prefixes)==len(prefixes):
            # No prefix is valid!
            return None, []

        else:
            webentity_id = self.__generated_web_entity_id()

            for prefix, [node, history] in valid_prefixes_index.items():
                node.read(node.block) # node update necessary
                node.set_webentity(webentity_id)
                node.write()

            return webentity_id, valid_prefixes_index.keys()

    def __create_webentity(self, prefix, expand=True, use_best_case=True):
        if expand: expanded_prefixes = self.expand_prefix(prefix)
        else: expanded_prefixes = [prefix]

        report = TraphWriteReport()
        webentity_id, valid_prefixes = self.__add_prefixes(expanded_prefixes, use_best_case)
        if webentity_id:
            report.created_webentities[webentity_id] = valid_prefixes

        return report

    def __apply_webentity_creation_rule(self, rule_prefix, lru):
        regexp = self.webentity_creation_rules[rule_prefix]
        match = regexp.search(lru)

        if not match:
            return None

        return match.group()

    def __apply_webentity_default_creation_rule(self, lru):

        regexp = self.default_webentity_creation_rule
        match = regexp.search(lru)

        if not match:
            return None

        return match.group()

    def __add_page(self, lru):
        node, history = self.lru_trie.add_page(lru)

        report = TraphWriteReport()

        # Expected behavior is:
        #   1) Retrieve all creation rules triggered 'above' in the trie
        #   2) Apply them in order to get CANDIDATE prefixes GENERATED by the rule
        #   3) Two cases:
        #      3a) All prefixes are smaller OR EQUAL (upper) than an existing prefix
        #          -> Nothing happens (webentity already exists)
        #      3b) A prefix is STRICTLY longer (lower) than existing prefixes
        #          -> apply the longest prefix as a new webentity

        # Retrieving the longest candidate prefix
        longest_candidate_prefix = ''
        for rule_prefix in history.rules_to_apply():
            candidate_prefix = self.__apply_webentity_creation_rule(rule_prefix, lru)

            if candidate_prefix and len(candidate_prefix) > len(longest_candidate_prefix):
                longest_candidate_prefix = candidate_prefix

        # In this case, the webentity already exists
        if longest_candidate_prefix and len(longest_candidate_prefix) <= history.webentity_position + 1:
            node.read(node.block) # update node
            return node, report

        # Else we need to expand the prefix and create relevant web entities
        if longest_candidate_prefix:
            report += self.__create_webentity(longest_candidate_prefix, expand=True)
            node.read(node.block) # update node
            return node, report

        # Nothing worked, we need to apply the default creation rule
        longest_candidate_prefix = self.__apply_webentity_default_creation_rule(lru)
        report += self.__create_webentity(longest_candidate_prefix, expand=True)
        node.read(node.block) # update node
        return node, report

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

    def add_webentity_creation_rule(self, rule_prefix, pattern, write_in_trie=True):
        rule_prefix = self.__encode(rule_prefix)

        self.webentity_creation_rules[rule_prefix] = re.compile(
            pattern,
            re.I
        )

        report = TraphWriteReport()

        if write_in_trie:
            node, history = self.lru_trie.add_lru(rule_prefix)
            if not node:
                raise Exception('Prefix not in tree: ' + rule_prefix)  # TODO: raise custom exception
            node.flag_as_webentity_creation_rule()
            node.write()
            # Spawn necessary web entities
            candidate_prefixes = set()
            for node2, lru in self.lru_trie.dfs_iter(node, rule_prefix):
                if node2.is_page():
                    _, add_report = self.__add_page(lru)
                    report += add_report

        return report

    def remove_webentity_creation_rule(self, rule_prefix):
        rule_prefix = self.__encode(rule_prefix)

        if not self.webentity_creation_rules[rule_prefix]:
            raise Exception('Prefix not in creation rules: ' + rule_prefix)  # TODO: raise custom exception
        del self.webentity_creation_rules[rule_prefix]

        node = self.lru_trie.lru_node(rule_prefix)
        if not node:
            raise Exception('Prefix %s cannot be found' % (prefix))  # TODO: raise custom exception
        node.unflag_as_webentity_creation_rule()
        node.write()

        return True

    def create_webentity(self, prefixes):
        prefixes = [self.__encode(prefix) for prefix in prefixes]

        report = TraphWriteReport()
        # Note: with use_best_case=False an error will be raised if any of the prefixes is invalid
        webentity_id, valid_prefixes = self.__add_prefixes(prefixes, use_best_case=False)
        report.created_webentities[webentity_id] = valid_prefixes
        return report

    def delete_webentity(self, weid, weid_prefixes, check_for_corruption=True):
        weid_prefixes = [self.__encode(weid_prefix) for weid_prefix in weid_prefixes]

        # Note: weid is ignored if no check for data consistency
        if check_for_corruption:
            prefix_index = {}
            for prefix in weid_prefixes:
                node = self.lru_trie.lru_node(prefix)
                if not node:
                    raise Exception('Prefix %s cannot be found' % (prefix))  # TODO: raise custom exception
                prefix_index.update({prefix: node})
                if not node.has_webentity() or node.webentity() != weid:
                    raise Exception('Prefix %s not attributed to webentity %s' % (prefix, weid))  # TODO: raise custom exception
        else:
            prefix_index = {}
            for prefix in weid_prefixes:
                node = self.lru_trie.lru_node(prefix)
                prefix_index.update({prefix: node})

        for prefix, node in prefix_index.items():
            node.unset_webentity()
            node.write()

        return True

    def add_prefix_to_webentity(self, prefix, weid):
        prefix = self.__encode(prefix)

        # check prefix
        node, history = self.lru_trie.add_lru(prefix)
        if node.has_webentity():
            raise Exception('Prefix %s already attributed to webentity %s' % (prefix, node.webentity()))  # TODO: raise custom exception
        else:
            node.set_webentity(weid)
            node.write()
            return True

    def remove_prefix_from_webentity(self, prefix, weid=False):
        prefix = self.__encode(prefix)

        # check prefix
        node, history = self.lru_trie.add_lru(prefix)
        if not weid or node.webentity() == weid:
            node.unset_webentity()
            node.write()
            return True
        else:
            raise Exception('Prefix %s not attributed to webentity %s' % (prefix, node.webentity()))  # TODO: raise custom exception

    def move_prefix_to_webentity(self, prefix, weid_target, weid_source=False):
        prefix = self.__encode(prefix)

        if self.remove_prefix_from_webentity(prefix, weid_source):
            return self.add_prefix_to_webentity(prefix, weid_target)
        return False

    def move_prefix_to_webentity_from_webentity(self, prefix, weid_target, weid_source=False):
        prefix = self.__encode(prefix)

        # Just an alias for clarity
        return self.move_prefix_to_webentity(prefix, weid_target, weid_source)

    def retrieve_prefix(self, lru):
        lru = self.__encode(lru)

        node, history = self.lru_trie.follow_lru(lru)
        if not node:
            raise Exception('LRU %s not in the traph' % (lru))  # TODO: raise custom exception
        if not history.webentity_prefix:
            raise Exception('No webentity prefix found for %s' % (lru))  # TODO: raise custom exception
        return history.webentity_prefix

    def retrieve_webentity(self, lru):
        lru = self.__encode(lru)

        node, history = self.lru_trie.follow_lru(lru)
        if not node:
            raise Exception('LRU %s not in the traph' % (lru))  # TODO: raise custom exception
        if not history.webentity:
            raise Exception('No webentity found for %s' % (lru))  # TODO: raise custom exception
        return history.webentity

    def get_webentity_by_prefix(self, prefix):
        prefix = self.__encode(prefix)

        node, history = self.lru_trie.follow_lru(prefix)
        if not node:
            raise Exception('LRU %s not in the traph' % (prefix))  # TODO: raise custom exception
        if not node.has_webentity():
            raise Exception('LRU %s is not a webentity prefix' % (prefix))  # TODO: raise custom exception
        return node.webentity()

    def get_webentity_pages(self, weid, prefixes):
        # Note: the prefixes are thoses of the webentity whose id is weid
        # No need to check
        pages = []
        for prefix in prefixes:
            prefix = self.__encode(prefix)

            starting_node, _ = self.lru_trie.follow_lru(prefix)
            if not starting_node:
                raise Exception('LRU %s not in the traph' % (prefix))  # TODO: raise custom exception
            for node, lru in self.lru_trie.webentity_dfs_iter(weid, starting_node, prefix):
                if node.is_page():
                    pages.append(lru)
        return pages

    def get_webentity_crawled_pages(self, weid, prefixes):
        # Note: the prefixes are thoses of the webentity whose id is weid
        # No need to check
        pages = []
        for prefix in prefixes:
            prefix = self.__encode(prefix)

            starting_node, _ = self.lru_trie.follow_lru(prefix)
            if not starting_node:
                raise Exception('LRU %s not in the traph' % (prefix))  # TODO: raise custom exception
            for node, lru in self.lru_trie.webentity_dfs_iter(weid, starting_node, prefix):
                if node.is_page() and node.is_crawled():
                    pages.append(lru)
        return pages

    def get_webentity_most_linked_pages(self, weid, prefixes, pages_count=10):
        # Note: the prefixes are thoses of the webentity whose id is weid
        # No need to check
        pages = []
        for prefix in prefixes:
            prefix = self.__encode(prefix)

            starting_node, _ = self.lru_trie.follow_lru(prefix)
            if not starting_node:
                raise Exception('LRU %s not in the traph' % (prefix))  # TODO: raise custom exception
            for node, lru in self.lru_trie.webentity_dfs_iter(weid, starting_node, prefix):
                if node.is_page():
                    # Iterate over link nodes
                    indegree = 0
                    # TODO: use a bounded heap for more efficiency
                    for linknode in self.link_store.link_nodes_iter(node.inlinks()):
                        indegree += 1
                    pages.append({'lru':lru, 'indegree':indegree})
        sorted_pages = sorted(pages, key=lambda p: p['indegree'])
        return [page['lru'] for page in sorted_pages[0:pages_count]]

    def get_webentity_parent_webentities(self, weid, prefixes):
        # Note: the prefixes are thoses of the webentity whose id is weid
        # No need to check
        weids = set()
        for prefix in prefixes:
            prefix = self.__encode(prefix)

            starting_node, _ = self.lru_trie.follow_lru(prefix)
            if not starting_node:
                raise Exception('LRU %s not in the traph' % (prefix))  # TODO: raise custom exception

            for node in self.lru_trie.node_parents_iter(starting_node):
                weid2 = node.webentity()
                if weid2 and weid2 > 0 and weid2 != weid:
                    weids.add(weid2)
        return weids

    def get_webentity_child_webentities(self, weid, prefixes):
        # TODO: return list of weid
        # Note: the prefixes are thoses of the webentity whose id is weid
        # No need to check
        pass

    def get_webentity_pagelinks(self, weid, prefixes, include_internal=False):
        # TODO: return list of [source_lru, target_lru, weight]
        # Note: the prefixes are thoses of the webentity whose id is weid
        # No need to check
        pass

    def get_webentities_links(self):
        graph = defaultdict(Counter)
        page_to_webentity = dict()

        # TODO: we should probably get a node helper another way
        target_node = LRUTrieNode(self.lru_trie_storage)

        for state in self.lru_trie.detailed_dfs_iter():
            node = state.node

            if not node.is_page() or not node.has_outlinks():
                continue

            source_webentity = state.current_webentity()
            page_to_webentity[node.block] = source_webentity

            # Iterating over the page's links
            links_block = node.outlinks()
            for link_node in self.link_store.link_nodes_iter(links_block):

                target_node.read(link_node.target())
                target_webentity = page_to_webentity.get(target_node.block)

                if target_webentity is None:
                    target_webentity = self.lru_trie.windup_lru_for_webentity(target_node)
                    page_to_webentity[target_node.block] = target_webentity

                # Adding to the graph
                graph[source_webentity][target_webentity] += link_node.weight()

        return graph



    def expand_prefix(self, prefix):
        prefix = self.__encode(prefix)

        return lru_variations(prefix)

    def add_page(self, lru):
        lru = self.__encode(lru)

        node, report = self.__add_page(lru)

        node.flag_as_crawled()
        node.write()

        return report

    def add_links(self, links):
        store = self.link_store
        report = TraphWriteReport()

        # TODO: this will need to return created web entities
        inlinks = defaultdict(list)
        outlinks = defaultdict(list)
        pages = dict()

        for source_page, target_page in links:
            source_page = self.__encode(source_page)
            target_page = self.__encode(target_page)

            # Adding pages
            if source_page not in pages:
                node, page_report = self.__add_page(source_page)
                report += page_report
                pages[source_page] = node
            if target_page not in pages:
                node, page_report = self.__add_page(target_page)
                report += page_report
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

        return report

    def close(self):

        # Cleanup
        if self.lru_trie_file:
            self.lru_trie_file.close()

        if self.link_store_file:
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

    def pages_iter(self):
        return self.lru_trie.pages_iter()

    def webentity_prefix_iter(self):
        return self.lru_trie.webentity_prefix_iter()
