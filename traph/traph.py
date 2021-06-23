# =============================================================================
# Traph Class
# =============================================================================
#
# Main class representing the Traph data structure.
#
import errno
import heapq
import os
import re
import warnings
from collections import defaultdict, Counter
from traph_write_report import TraphWriteReport
from traph_iterator_state import TraphIteratorState, run_iterator
from storage import FileStorage, MemoryStorage
from lru_trie import LRUTrie, LRU_TRIE_NODE_BLOCK_SIZE
from link_store import LinkStore, LINK_STORE_NODE_BLOCK_SIZE

from helpers import (
    lru_variations,
    build_pagination_token,
    parse_pagination_token
)


# Exceptions
class TraphException(Exception):
    pass


# Main class
class Traph(object):

    # =========================================================================
    # Constructor
    # =========================================================================
    def __init__(self, folder=None, overwrite=False, encoding='utf-8',
                 debug=False, default_webentity_creation_rule=None,
                 webentity_creation_rules=None):

        # Handling encoding
        self.encoding = encoding

        # Debugging mode
        if debug:
            if not default_webentity_creation_rule:
                default_webentity_creation_rule = ''
            if not webentity_creation_rules:
                webentity_creation_rules = {}
        else:

            # Ensuring the creation rules are set
            if not isinstance(default_webentity_creation_rule, basestring):
                raise TraphException('Given default webentity creation rule is not a string!')

            if not isinstance(webentity_creation_rules, dict):
                raise TraphException('Given webentity creation rules is not a dict!')
                # TODO: check if each value is correctly a string

        # Files
        self.folder = folder
        self.lru_trie_file = None
        self.link_store_file = None
        self.lru_trie_path = None
        self.link_store_path = None

        create = overwrite
        self.in_memory = not bool(folder)

        # Solving paths
        if not self.in_memory:
            self.lru_trie_path = os.path.join(folder, 'lru_trie.dat')
            self.link_store_path = os.path.join(folder, 'link_store.dat')

            # Ensuring the given folder exists
            try:
                os.makedirs(folder)
            except OSError as exception:
                if exception.errno == errno.EEXIST and os.path.isdir(folder):
                    pass
                else:
                    raise

            # Testing existence of files
            lru_trie_file_exists = os.path.isfile(self.lru_trie_path)
            link_store_file_exists = os.path.isfile(self.link_store_path)

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

            self.lru_trie_file = open(self.lru_trie_path, flags)
            self.link_store_file = open(self.link_store_path, flags)

            self.lru_trie_storage = FileStorage(
                LRU_TRIE_NODE_BLOCK_SIZE,
                self.lru_trie_file
            )

            self.links_store_storage = FileStorage(
                LINK_STORE_NODE_BLOCK_SIZE,
                self.link_store_file
            )

            # Checking for corruption
            if not create and self.lru_trie_storage.check_for_corruption():
                raise TraphException(
                    'File corrupted: `lru_trie.dat`'
                )

            if not create and self.links_store_storage.check_for_corruption():
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
        if not debug:
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
            node, history = self.lru_trie.add_lru(prefix, flag_can_have_child_webentities=True)

            if node.has_webentity():
                invalid_prefixes.append(prefix)
            else:
                valid_prefixes_index.update({prefix: [node, history]})

        if len(invalid_prefixes) > 0 and not use_best_case:
            raise TraphException('Some prefixes were already set: %s' % (invalid_prefixes))

        elif len(invalid_prefixes) == len(prefixes):
            # No prefix is valid!
            return None, []

        else:
            webentity_id = self.__generated_web_entity_id()

            for prefix, [node, history] in valid_prefixes_index.items():
                node.refresh()  # node update necessary
                node.set_webentity(webentity_id)
                node.write()

            return webentity_id, valid_prefixes_index.keys()

    def __create_webentity(self, prefix, expand=True, use_best_case=True):
        if expand:
            expanded_prefixes = self.expand_prefix(prefix)
        else:
            expanded_prefixes = [prefix]

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

    def __add_page(self, lru, crawled=False):
        node, history = self.lru_trie.add_page(lru, crawled=crawled)

        report = TraphWriteReport()

        if history.page_was_created:
            report.nb_created_pages += 1

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
        if len(longest_candidate_prefix) <= history.webentity_position:
            node.refresh()  # update node
            return node, report

        # Else we need to expand the prefix and create relevant web entities
        if longest_candidate_prefix:
            report += self.__create_webentity(longest_candidate_prefix, expand=True)
            node.refresh()  # update node
            return node, report

        # Nothing worked, we need to apply the default creation rule
        longest_candidate_prefix = self.__apply_webentity_default_creation_rule(lru)

        # If the default rule failed to find a prefix, we emit an error
        if not longest_candidate_prefix:
            warnings.warn(
                'Default rule failed to find a prefix for "%s"!' % lru,
                RuntimeWarning
            )
        else:
            report += self.__create_webentity(longest_candidate_prefix, expand=True)

        node.refresh()  # update node
        return node, report

    # =========================================================================
    # Public interface
    # =========================================================================
    def add_webentity_creation_rule_iter(self, rule_prefix, pattern, write_in_trie=True):
        '''
        Note: write_in_trie has 2 effects: store the rule in the trie, and apply it to existing entities.
        write_in_trie=False is essentially for init on an existing traph.

        Note 2: it seems obvious from the api design but let's restate it:
        We can only have one rule for each prefix (or none).
        '''
        rule_prefix = self.__encode(rule_prefix)

        self.webentity_creation_rules[rule_prefix] = re.compile(
            pattern,
            re.I
        )

        report = TraphWriteReport()
        state = TraphIteratorState()

        if write_in_trie:
            node, history = self.lru_trie.add_lru(rule_prefix)
            if not node:
                raise TraphException('Prefix not in tree: ' + rule_prefix)
            node.flag_as_webentity_creation_rule()
            node.write()
            # Spawn necessary web entities
            candidate_prefixes = set()
            for node2, lru in self.lru_trie.dfs_iter(node, rule_prefix):
                if node2.is_page():
                    _, add_report = self.__add_page(lru)
                    report += add_report

                if state.should_yield():
                    yield state

        yield state.finalize(report)

    def add_webentity_creation_rule(self, rule_prefix, pattern, write_in_trie=True):
        return run_iterator(self.add_webentity_creation_rule_iter(rule_prefix, pattern, write_in_trie=write_in_trie))

    def remove_webentity_creation_rule(self, rule_prefix):
        rule_prefix = self.__encode(rule_prefix)

        if not self.webentity_creation_rules[rule_prefix]:
            raise TraphException('Prefix not in creation rules: ' + rule_prefix)
        del self.webentity_creation_rules[rule_prefix]

        node = self.lru_trie.lru_node(rule_prefix)
        if not node:
            raise TraphException('Prefix %s cannot be found' % (prefix))
        node.unflag_as_webentity_creation_rule()
        node.write()

        return True

    def create_webentity(self, prefixes):
        '''
        Note: will raise an error if any of the prefixes is already defining an existing entity
        '''
        prefixes = [self.__encode(prefix) for prefix in prefixes]

        report = TraphWriteReport()
        # Note: with use_best_case=False an error will be raised if any of the prefixes is invalid
        webentity_id, valid_prefixes = self.__add_prefixes(prefixes, use_best_case=False)
        report.created_webentities[webentity_id] = valid_prefixes
        return report

    def delete_webentity(self, weid, weid_prefixes, check_for_corruption=True):
        '''
        Note: weid is only useful to check data consistency, but not strictly necessary to the method.
        It there is no weid, a consistency check will be skipped but the method will execute regardless.
        '''
        weid_prefixes = [self.__encode(weid_prefix) for weid_prefix in weid_prefixes]

        # Note: weid is ignored if no check for data consistency
        if check_for_corruption:
            prefix_index = {}
            for prefix in weid_prefixes:
                node = self.lru_trie.lru_node(prefix)
                if not node:
                    raise TraphException('Prefix %s cannot be found' % (prefix))
                prefix_index.update({prefix: node})
                if not node.has_webentity() or node.webentity() != weid:
                    raise TraphException('Prefix %s not attributed to webentity %s' % (prefix, weid))
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
        node, history = self.lru_trie.add_lru(prefix, flag_can_have_child_webentities=True)
        if node.has_webentity():
            raise TraphException('Prefix %s already attributed to webentity %s' % (prefix, node.webentity()))
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
            raise TraphException('Prefix %s not attributed to webentity %s' % (prefix, node.webentity()))

    def move_prefix_to_webentity(self, prefix, weid_target, weid_source=False):
        '''
        Note: pay attention to the unintuitive order of arguments.
        You may prefer the more explicit alias move_prefix_to_webentity_from_webentity
        '''
        prefix = self.__encode(prefix)

        if self.remove_prefix_from_webentity(prefix, weid_source):
            return self.add_prefix_to_webentity(prefix, weid_target)
        return False

    def move_prefix_to_webentity_from_webentity(self, prefix, weid_target, weid_source=False):
        '''
        A more explicit alias of move_prefix_to_webentity
        '''
        return self.move_prefix_to_webentity(prefix, weid_target, weid_source)

    def retrieve_prefix(self, lru):
        '''
        Returns the closest prefix to contain the LRU
        (the prefix defining the webentity that the LRU belongs to)
        Note: does not apply creation rules. For that feature see get_potential_prefix()
        '''
        lru = self.__encode(lru)

        node, history = self.lru_trie.follow_lru(lru)

        # NOTE: it should not throw here.
        # if not node:
        #     raise TraphException('LRU %s not in the traph' % (lru))
        if not history.webentity_prefix:
            raise TraphException('No webentity prefix found for %s' % (lru))
        return history.webentity_prefix

    def get_potential_prefix(self, lru):
        '''
        Returns the longest of prefixes or "potential prefixes" ie. from creation rules.
        Very similar to internal method __add_page except it does not add the lru.
        '''
        lru = self.__encode(lru)
        node, history = self.lru_trie.follow_lru(lru)

        # Retrieving the longest candidate prefix
        longest_candidate_prefix = ''
        for rule_prefix in history.rules_to_apply():
            candidate_prefix = self.__apply_webentity_creation_rule(rule_prefix, lru)

            if candidate_prefix and len(candidate_prefix) > len(longest_candidate_prefix):
                longest_candidate_prefix = candidate_prefix

        # If the longest rules prefix is shorter than the webentity prefix, or there is no rules prefix
        if len(longest_candidate_prefix) <= history.webentity_position:
            return history.webentity_prefix

        # If there is a rules prefix and it is longer than the webentity prefix
        if longest_candidate_prefix:
            return longest_candidate_prefix

        # If there is neither a webentity prefix nor a rules prefix, look for the default rule
        longest_candidate_prefix = self.__apply_webentity_default_creation_rule(lru)

        # If the default rule failed to find a prefix, we emit an error
        if not longest_candidate_prefix:
            warnings.warn(
                'Default rule failed to find a prefix for "%s"!' % lru,
                RuntimeWarning
            )
            return False
        else:
            return longest_candidate_prefix

    def retrieve_webentity(self, lru):
        '''
        Returns the closest webentity id to contain the LRU
        (the webentity it belongs to)
        '''
        lru = self.__encode(lru)

        node, history = self.lru_trie.follow_lru(lru)

        # NOTE: it should not throw here.
        # if not node:
        #     raise TraphException('LRU %s not in the traph' % (lru))
        if not history.webentity:
            raise TraphException('No webentity found for %s' % (lru))
        return history.webentity

    def get_webentity_by_prefix(self, prefix):
        prefix = self.__encode(prefix)

        node = self.lru_trie.lru_node(prefix)
        if not node:
            raise TraphException('LRU %s not in the traph' % (prefix))
        if not node.has_webentity():
            raise TraphException('LRU %s is not a webentity prefix' % (prefix))
        return node.webentity()

    def get_webentity_pages_iter(self, weid, prefixes):
        '''
        Note: the prefixes are supposed to match the webentity id. We do not check.
        '''
        state = TraphIteratorState()
        pages = []
        for node, lru in self.webentity_page_nodes_iter(weid, prefixes):
            pages.append({
                'lru': lru,
                'crawled': node.is_crawled()
            })

            if state.should_yield(2000):
                yield state

        yield state.finalize(pages)

    def get_webentity_pages(self, weid, prefixes):
        return run_iterator(self.get_webentity_pages_iter(weid, prefixes))

    def paginate_webentity_pages(self, weid, prefixes,
                                 page_count=None, pagination_token=None,
                                 crawled_only=False):

        if page_count is not None:
            assert page_count > 0

        # NOTE: we iterate on k + 1 pages to be sure to exhaust the inorder
        # traversal and not require of the user to make an additional pointless
        # pagination call to finally find that the traversal is over
        k = page_count + 1 if page_count is not None else None

        start_i = 0
        pagination_path = None
        pages = []
        n = 0
        c = 0
        last_path = None
        last_path_i = None

        if pagination_token:
            start_i, pagination_path = parse_pagination_token(pagination_token)

        for i in range(start_i, len(prefixes)):
            current_prefix = self.__encode(prefixes[i])

            starting_node = self.lru_trie.lru_node(current_prefix)

            if not starting_node:
                raise TraphException('LRU %s not in the traph' % (current_prefix))

            generator = self.lru_trie.webentity_inorder_iter(
                starting_node,
                current_prefix,
                pagination_path=pagination_path
            )

            for node, lru, path in generator:
                if not node.is_page():
                    continue

                crawled = node.is_crawled()

                if crawled_only and not crawled:
                    continue

                n += 1

                if k is not None and n >= k:
                    return {
                        'done': False,
                        'count': n - 1,
                        'count_crawled': c,
                        'pages': pages[:n - 1],
                        'token': build_pagination_token(last_path_i, last_path)
                    }

                if crawled:
                    c += 1

                pages.append({
                    'lru': lru,
                    'crawled': crawled
                })

                last_path = path
                last_path_i = i

            # We reset the pagination path for next prefix
            pagination_path = None

        return {
            'done': True,
            'count': n,
            'count_crawled': c,
            'pages': pages
        }

        return result

    def get_webentity_crawled_pages_iter(self, weid, prefixes):
        '''
        Note: the prefixes are supposed to match the webentity id. We do not check.
        '''
        state = TraphIteratorState()
        pages = []
        for node, lru in self.webentity_page_nodes_iter(weid, prefixes):
            if node.is_crawled():
                pages.append({
                    'lru': lru,
                    'crawled': True
                })

            if state.should_yield(2000):
                yield state

        yield state.finalize(pages)

    def get_webentity_crawled_pages(self, weid, prefixes):
        return run_iterator(self.get_webentity_crawled_pages_iter(weid, prefixes))

    def get_webentity_most_linked_pages_iter(self, weid, prefixes, pages_count=10, max_depth=None):
        '''
        Returns a list of objects {lru:, indegree:}
        Note: the prefixes are supposed to match the webentity id. We do not check.
        '''
        state = TraphIteratorState()
        pages = []
        c = 0
        for prefix in prefixes:
            prefix = self.__encode(prefix)

            starting_node = self.lru_trie.lru_node(prefix)
            if not starting_node:
                raise TraphException('LRU %s not in the traph' % (prefix))

            for node, lru in self.lru_trie.webentity_dfs_iter(starting_node, prefix, max_depth):
                if node.is_page():

                    # Iterate over link nodes
                    indegree = 0

                    for linknode in self.link_store.link_nodes_iter(node.inlinks()):
                        indegree += 1

                    c += 1
                    heapq.heappush(pages, (indegree, c, lru))

                    if len(pages) > pages_count:
                        heapq.heappop(pages)

                if state.should_yield(2000):
                    yield state

        sorted_pages = range(len(pages))
        i = len(pages) - 1

        while len(pages):
            page = heapq.heappop(pages)
            sorted_pages[i] = {'lru': page[2], 'indegree': page[0]}
            i -= 1

        yield state.finalize(sorted_pages)

    def get_webentity_most_linked_pages(self, weid, prefixes, pages_count=10, max_depth=None):
        return run_iterator(self.get_webentity_most_linked_pages_iter(weid, prefixes, pages_count=pages_count, max_depth=max_depth))

    def get_webentity_parent_webentities(self, weid, prefixes):
        '''
        Note: the prefixes are supposed to match the webentity id. We do not check.
        '''
        weids = set()
        for prefix in prefixes:
            prefix = self.__encode(prefix)

            starting_node = self.lru_trie.lru_node(prefix)
            if not starting_node:
                raise TraphException('LRU %s not in the traph' % (prefix))

            for node in self.lru_trie.node_parents_iter(starting_node):
                weid2 = node.webentity()
                if weid2 and weid2 > 0 and weid2 != weid:
                    weids.add(weid2)

        return list(weids)

    def get_webentity_child_webentities_iter(self, weid, prefixes):
        '''
        Note: the prefixes are supposed to match the webentity id. We do not check.
        '''
        state = TraphIteratorState()
        weids = set()
        for prefix in prefixes:
            prefix = self.__encode(prefix)

            starting_node = self.lru_trie.lru_node(prefix)
            if not starting_node:
                raise TraphException('LRU %s not in the traph' % (prefix))

            for node, _ in self.lru_trie.dfs_iter(starting_node, prefix, skip_childless_paths=True):
                weid2 = node.webentity()
                if weid2 and weid2 > 0 and weid2 != weid:
                    weids.add(weid2)

                if state.should_yield(5000):
                    yield state

        yield state.finalize(list(weids))

    def get_webentity_child_webentities(self, weid, prefixes):
        return run_iterator(self.get_webentity_child_webentities_iter(weid, prefixes))

    def get_webentity_pagelinks_iter(self, weid, prefixes, include_inbound=False, include_internal=True, include_outbound=False):
        '''
        Returns all or part of: pagelinks to the entity, internal pagelinks, pagelinks out of the entity.
        Default is only internal pagelinks.
        Note: the prefixes are supposed to match the webentity id. We do not check.
        '''

        # TODO: Can be optimized caching windups

        if not include_internal and not include_outbound and not include_inbound:
            raise TraphException('At least one of include _internal or include_outbound or include_inbound should be true')

        state = TraphIteratorState()
        pagelinks = []

        source_node = self.lru_trie.node()
        target_node = self.lru_trie.node()

        for prefix in prefixes:
            prefix = self.__encode(prefix)

            starting_node = self.lru_trie.lru_node(prefix)
            if not starting_node:
                raise TraphException('LRU %s not in the traph' % (prefix))

            for node, lru in self.lru_trie.webentity_dfs_iter(starting_node, prefix):

                if not node.is_page():
                    continue

                # Iterating over the page's outlinks
                if node.has_outlinks() and (include_outbound or include_internal):
                    links_block = node.outlinks()
                    for link_node in self.link_store.link_nodes_iter(links_block):

                        target_node.read(link_node.target())
                        target_lru = self.lru_trie.windup_lru(target_node.block)
                        target_webentity = self.lru_trie.windup_lru_for_webentity(target_node)

                        if (include_outbound and target_webentity != weid) or (include_internal and target_webentity == weid):
                            pagelinks.append([lru, target_lru, link_node.weight()])

                        if state.should_yield(5000):
                            yield state

                # Iterating over the page's inlinks
                if node.has_inlinks() and include_inbound:
                    links_block = node.inlinks()
                    for link_node in self.link_store.link_nodes_iter(links_block):

                        source_node.read(link_node.target())
                        source_lru = self.lru_trie.windup_lru(source_node.block)
                        source_webentity = self.lru_trie.windup_lru_for_webentity(source_node)

                        if source_webentity != weid:
                            pagelinks.append([source_lru, lru, link_node.weight()])

                        if state.should_yield(5000):
                            yield state

        yield state.finalize(pagelinks)

    def get_webentity_pagelinks(self, weid, prefixes, include_inbound=False, include_internal=True, include_outbound=False):
        return run_iterator(self.get_webentity_pagelinks_iter(weid, prefixes, include_inbound=include_inbound, include_internal=include_internal, include_outbound=include_outbound))

    def paginate_webentity_pagelinks(self, weid, prefixes,
                                     include_internal=True, include_outbound=False,
                                     source_page_count=None, pagination_token=None):

        if source_page_count is not None:
            assert source_page_count > 0

        if not include_internal and not include_outbound:
            raise TraphException('At least one of include_internal or include_outbound should be true')

        target_node = self.lru_trie.node()
        start_i = 0
        pagination_path = None
        pagelinks = []
        n = 0
        c = 0
        last_path = None
        last_path_i = None

        if pagination_token:
            start_i, pagination_path = parse_pagination_token(pagination_token)

        for i in range(start_i, len(prefixes)):
            current_prefix = self.__encode(prefixes[i])

            starting_node = self.lru_trie.lru_node(current_prefix)

            if not starting_node:
                raise TraphException('LRU %s not in the traph' % (current_prefix))

            generator = self.lru_trie.webentity_inorder_iter(
                starting_node,
                current_prefix,
                pagination_path=pagination_path
            )

            # Iterating over the prefix's lrus in order
            for node, lru, path in generator:
                if not node.is_page():
                    continue

                if not node.has_outlinks():
                    last_path = path
                    continue

                # Iterating over the page's outlinks
                links_block = node.outlinks()
                newlinks = []

                for link_node in self.link_store.link_nodes_iter(links_block):
                    target_node.read(link_node.target())
                    target_webentity = self.lru_trie.windup_lru_for_webentity(target_node)

                    if (include_outbound and target_webentity != weid) or (include_internal and target_webentity == weid):
                        target_lru = self.lru_trie.windup_lru(target_node.block)
                        newlinks.append([lru, target_lru, link_node.weight()])

                if newlinks:
                    n += 1

                    if source_page_count is not None and n > source_page_count:
                        return {
                            'done': False,
                            'count_sourcepages': n - 1,
                            'count_pagelinks': len(pagelinks),
                            'pagelinks': pagelinks,
                            'token': build_pagination_token(last_path_i, last_path)
                        }

                    pagelinks += newlinks

                last_path = path
                last_path_i = i

            # We reset the pagination path for next prefix
            pagination_path = None

        return {
            'done': True,
            'count_sourcepages': n,
            'count_pagelinks': len(pagelinks),
            'pagelinks': pagelinks
        }

    def get_webentity_outlinks_iter(self, weid, prefixes):
        '''
        Returns the list of cited web entities
        Note: the prefixes are supposed to match the webentity id. We do not check.
        '''

        state = TraphIteratorState()
        done_blocks = set()
        weids = set()

        target_node = self.lru_trie.node()

        for prefix in prefixes:
            prefix = self.__encode(prefix)

            starting_node = self.lru_trie.lru_node(prefix)
            if not starting_node:
                raise TraphException('LRU %s not in the traph' % (prefix))

            for node, lru in self.lru_trie.webentity_dfs_iter(starting_node, prefix):

                if not node.is_page():
                    continue

                # Iterating over the page's outlinks
                if node.has_outlinks():
                    links_block = node.outlinks()
                    for link_node in self.link_store.link_nodes_iter(links_block):
                        target_node.read(link_node.target())
                        if target_node.block not in done_blocks:
                            target_webentity = self.lru_trie.windup_lru_for_webentity(target_node)
                            done_blocks.add(target_node.block)
                            weids.add(target_webentity)

                        if state.should_yield(5000):
                            yield state

        yield state.finalize(weids)

    def get_webentity_outlinks(self, weid, prefixes):
        return run_iterator(self.get_webentity_outlinks_iter(weid, prefixes))

    def get_webentity_outdegree(self, weid, prefixes):
        '''
        Convenience method relying on get_webentity_outlinks (thus NOT more efficient)
        Note: the prefixes are supposed to match the webentity id. We do not check.
        '''
        # TODO: optimize

        return len(self.get_webentity_outlinks(weid, prefixes))

    def get_webentity_inlinks_iter(self, weid, prefixes):
        '''
        Returns the list of citing web entities
        Note: the prefixes are supposed to match the webentity id. We do not check.
        '''

        state = TraphIteratorState()
        done_blocks = set()
        weids = set()

        source_node = self.lru_trie.node()

        for prefix in prefixes:
            prefix = self.__encode(prefix)

            starting_node = self.lru_trie.lru_node(prefix)
            if not starting_node:
                raise TraphException('LRU %s not in the traph' % (prefix))

            for node, lru in self.lru_trie.webentity_dfs_iter(starting_node, prefix):

                if not node.is_page():
                    continue

                # Iterating over the page's inlinks
                if node.has_inlinks():
                    links_block = node.inlinks()
                    for link_node in self.link_store.link_nodes_iter(links_block):
                        source_node.read(link_node.target())
                        if source_node.block not in done_blocks:
                            source_webentity = self.lru_trie.windup_lru_for_webentity(source_node)
                            done_blocks.add(source_node.block)
                            weids.add(source_webentity)

                        if state.should_yield(5000):
                            yield state

        yield state.finalize(weids)

    def get_webentity_inlinks(self, weid, prefixes):
        return run_iterator(self.get_webentity_inlinks_iter(weid, prefixes))

    def get_webentity_indegree(self, weid, prefixes):
        '''
        Convenience method relying on get_webentity_inlinks (thus NOT more efficient)
        Note: the prefixes are supposed to match the webentity id. We do not check.
        '''
        # TODO: optimize

        return len(self.get_webentity_inlinks(weid, prefixes))

    def get_webentity_degree(self, weid, prefixes):
        '''
        Note: relies on get_webentity_inlinks() and get_webentity_outlinks(),
        thus not more efficient than calling these.
        '''
        # TODO: optimize

        return self.get_webentity_indegree(weid, prefixes) + self.get_webentity_outdegree(weid, prefixes)

    def get_page_links(self, lru, include_inbound=True, include_internal=True, include_outbound=True):
        lru = self.__encode(lru)
        node = self.lru_trie.lru_node(lru)

        if not node or not node.is_page():
            return []

        pagelinks = []

        source_node = self.lru_trie.node()
        target_node = self.lru_trie.node()

        # Iterating over the page's outlinks
        if node.has_outlinks() and (include_outbound or include_internal):
            links_block = node.outlinks()
            for link_node in self.link_store.link_nodes_iter(links_block):

                target_node.read(link_node.target())
                target_lru = self.lru_trie.windup_lru(target_node.block)

                if (include_outbound and target_lru != lru) or (include_internal and target_lru == lru):
                    pagelinks.append([lru, target_lru, link_node.weight()])

        # Iterating over the page's inlinks
        if node.has_inlinks() and include_inbound:
            links_block = node.inlinks()
            for link_node in self.link_store.link_nodes_iter(links_block):

                source_node.read(link_node.target())
                source_lru = self.lru_trie.windup_lru(source_node.block)

                if source_lru != lru:
                    pagelinks.append([source_lru, lru, link_node.weight()])

        return pagelinks

    def get_page_indegree(self, lru, weighted=False):
        '''
        Convenience method relying on get_page_links (thus NOT more efficient)
        '''
        if weighted:
            total = 0
            for _, _, weight in self.get_page_links(lru, include_inbound=True, include_internal=False, include_outbound=False):
                total += weight
            return total
        else:
            return len(self.get_page_links(lru, include_inbound=True, include_internal=False, include_outbound=False))

    def get_page_outdegree(self, lru, weighted=False):
        '''
        Convenience method relying on get_page_links (thus NOT more efficient)
        '''
        if weighted:
            total = 0
            for _, _, weight in self.get_page_links(lru, include_inbound=False, include_internal=False, include_outbound=True):
                total += weight
            return total
        else:
            return len(self.get_page_links(lru, include_inbound=False, include_internal=False, include_outbound=True))

    def get_page_degree(self, lru, weighted=False):
        '''
        Convenience method relying on get_page_links (thus NOT more efficient)
        '''
        if weighted:
            total = 0
            for _, _, weight in self.get_page_links(lru, include_inbound=True, include_internal=True, include_outbound=True):
                total += weight
            return total
        else:
            return len(self.get_page_links(lru, include_inbound=True, include_internal=True, include_outbound=True))

    def get_webentities_links_slow_iter(self, out=True, include_auto=False):
        '''
        This method should be slower than the regular version but lighter in
        memory as it does not retain a full map of pages association to
        webentities but only the least recently used ones.
        '''
        graph = defaultdict(Counter)
        page_to_webentity = dict()
        state = TraphIteratorState()
        target_node = self.lru_trie.node()

        # Iterating over all pages
        for node, source_webentity in self.lru_trie.dfs_with_webentity_iter():

            if not node.is_page() or not node.has_links(out=out):
                continue

            if not source_webentity:
                continue

            page_to_webentity[node.block] = source_webentity

            # Iterating over the page's links
            links_block = node.links(out=out)
            for link_node in self.link_store.link_nodes_iter(links_block):

                target_block = link_node.target()
                target_webentity = page_to_webentity.get(target_block)

                if target_webentity is None:
                    target_node.read(target_block)
                    target_webentity = self.lru_trie.windup_lru_for_webentity(target_node)

                    # Beware: it's possible that we could not find a webentity
                    if not target_webentity:
                        continue

                    page_to_webentity[target_block] = target_webentity

                # Allowing auto links?
                if not include_auto and source_webentity == target_webentity:
                    continue

                # Adding to the graph
                graph[source_webentity][target_webentity] += link_node.weight()

                if state.should_yield(5000):
                    yield state

        yield state.finalize(graph)

    def get_webentities_links_iter(self, out=True, include_auto=False):
        '''
        This method should be faster than the slow version because it avoids
        unnecessary upward traversal.

        Note that it is also possible to solve the links right away and store
        them to solve their webentities later but this is most costly in RAM.
        '''
        graph = defaultdict(Counter)
        page_to_webentity = dict()
        link_pointers = []
        state = TraphIteratorState()

        # Solving the page => webentity relation
        for node, source_webentity in self.lru_trie.dfs_with_webentity_iter():
            if not node.is_page():
                continue

            if not source_webentity:
                continue

            crawled_status = 'crawled' if node.is_crawled() else 'uncrawled'
            graph[source_webentity]['pages_' + crawled_status] += 1

            page_to_webentity[node.block] = source_webentity

            if node.has_links(out=out):
                link_pointers.append((source_webentity, node.links(out=out)))

            if state.should_yield():
                yield state

        # Computing the links
        for source_webentity, links_block in link_pointers:

            for link_node in self.link_store.link_nodes_iter(links_block):
                target_webentity = page_to_webentity.get(link_node.target())

                # The target page might not have a target webentity
                if not target_webentity:
                    continue

                if not include_auto and source_webentity == target_webentity:
                    continue

                # Adding to the graph
                graph[source_webentity][target_webentity] += link_node.weight()

                if state.should_yield(5000):
                    yield state

        yield state.finalize(graph)

    def get_webentities_inlinks_iter(self, include_auto=False):
        return self.get_webentities_links_iter(out=False, include_auto=include_auto)

    def get_webentities_outlinks_iter(self, include_auto=False):
        return self.get_webentities_links_iter(out=True, include_auto=include_auto)

    def get_webentities_links(self, out=True, include_auto=False):
        return run_iterator(self.get_webentities_links_iter(out=out, include_auto=include_auto))

    def get_webentities_links_slow(self, out=True, include_auto=False):
        return run_iterator(self.get_webentities_links_slow_iter(out=out, include_auto=include_auto))

    def get_webentities_inlinks(self, include_auto=False):
        return self.get_webentities_links(out=False, include_auto=include_auto)

    def get_webentities_outlinks(self, include_auto=False):
        return self.get_webentities_links(out=True, include_auto=include_auto)

    def expand_prefix(self, prefix):
        prefix = self.__encode(prefix)

        return lru_variations(prefix)

    def add_page(self, lru, crawled=False):
        '''
        Returns a webentity creation report as {created_webentities: {weid:[prefixes], ...}}
        '''
        lru = self.__encode(lru)

        node, report = self.__add_page(lru, crawled=crawled)

        return report

    def add_pages(self, lrus, crawled=False):

        report = TraphWriteReport()

        for lru in lrus:
            lru = self.__encode(lru)

            node, page_report = self.__add_page(lru, crawled=crawled)
            report += page_report

            node.flag_as_crawled()
            node.write()

        return report

    def add_links(self, links):
        store = self.link_store
        report = TraphWriteReport()

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

            # Refreshing node's data
            source_node.refresh()
            target_blocks = (pages[target_page].block for target_page in target_pages)
            store.add_outlinks(source_node, target_blocks)

        for target_page, source_pages in inlinks.items():
            target_node = pages[target_page]

            # Refreshing node's data
            target_node.refresh()
            source_blocks = (pages[source_page].block for source_page in source_pages)
            store.add_inlinks(target_node, source_blocks)

        return report

    def index_batch_crawl_iter(self, data):
        '''
        data must be a multimap 'source_lru' => 'target_lrus'
        '''
        store = self.link_store
        state = TraphIteratorState()
        report = TraphWriteReport()
        pages = dict()
        inlinks = defaultdict(list)

        for source_page, target_pages in data.items():
            source_page = self.__encode(source_page)

            # We need to add the page
            if source_page not in pages:
                source_node, source_page_report = self.__add_page(source_page, crawled=True)
                report += source_page_report
                pages[source_page] = source_node
            else:
                source_node = pages[source_page]

                if not source_node.is_crawled():
                    source_node.refresh()
                    source_node.flag_as_crawled()
                    source_node.write()

            target_blocks = []

            for target_page in target_pages:
                target_page = self.__encode(target_page)

                if target_page not in pages:
                    target_node, target_page_report = self.__add_page(target_page)
                    report += target_page_report
                    pages[target_page] = target_node
                    target_blocks.append(target_node.block)

                    if state.should_yield(200):
                        yield state

                else:
                    target_blocks.append(pages[target_page].block)

                # TODO: possible to store block as value rather
                inlinks[target_page].append(source_page)

            source_node.refresh()
            store.add_outlinks(source_node, target_blocks)

        for target_page, source_pages in inlinks.items():
            target_node = pages[target_page]
            target_node.refresh()
            source_blocks = (pages[source_page].block for source_page in source_pages)
            store.add_inlinks(target_node, source_blocks)

            if state.should_yield():
                yield state

        yield state.finalize(report)

    def index_batch_crawl(self, data):
        return run_iterator(self.index_batch_crawl_iter(data))

    def close(self):

        # Cleanup
        if self.lru_trie_file:
            self.lru_trie_file.close()

        if self.link_store_file:
            self.link_store_file.close()

    def clear(self, default_webentity_creation_rule=None, webentity_creation_rules=None):
        self.close()

        if self.in_memory:
            self.lru_trie_storage.clear()
            self.links_store_storage.clear()
        else:
            self.lru_trie_file = open(self.lru_trie_path, 'wb+')
            self.link_store_file = open(self.link_store_path, 'wb+')

            self.lru_trie_storage.file = self.lru_trie_file
            self.links_store_storage.file = self.link_store_file

        # LRU Trie re-initialization
        self.lru_trie = LRUTrie(self.lru_trie_storage, encoding=self.encoding)

        # Link Store re-initialization
        self.link_store = LinkStore(self.links_store_storage)

        # Updating creation rules?
        # TODO: this code is basically duplicated from __init__ maybe refactor?
        if default_webentity_creation_rule is not None:
            self.default_webentity_creation_rule = re.compile(
                default_webentity_creation_rule,
                re.I
            )

        if webentity_creation_rules is not None:
            self.webentity_creation_rules = {}

            for prefix, pattern in webentity_creation_rules.items():
                self.add_webentity_creation_rule(prefix, pattern, True)

    # =========================================================================
    # Iteration methods
    # =========================================================================
    def links_iter(self, out=True):
        for page_node, lru in self.lru_trie.pages_iter():
            if not page_node.links(out=out):
                continue

            for link_node in self.link_store.link_nodes_iter(page_node.links(out=out)):
                yield lru, self.lru_trie.windup_lru(link_node.target())

    def pages_iter(self):
        return self.lru_trie.pages_iter()

    def webentity_prefix_iter(self):
        return self.lru_trie.webentity_prefix_iter()

    # TODO: weid arg useless
    def webentity_page_nodes_iter(self, weid, prefixes):
        '''
        Note: the prefixes are supposed to match the webentity id. We do not check.
        '''
        for prefix in prefixes:
            prefix = self.__encode(prefix)

            starting_node = self.lru_trie.lru_node(prefix)

            if not starting_node:
                raise TraphException('LRU %s not in the traph' % (prefix))

            for node, lru in self.lru_trie.webentity_dfs_iter(starting_node, prefix):
                if node.is_page():
                    yield node, lru

    # =========================================================================
    # Counting methods
    # =========================================================================
    def count_pages(self):
        return self.lru_trie.count_pages()

    def count_crawled_pages(self):
        return self.lru_trie.count_crawled_pages()

    def count_links(self):
        return self.link_store.count_links()

    def metrics(self):
        return {
            'lru_trie': self.lru_trie.metrics(),
            'link_store': self.link_store.metrics()
        }
