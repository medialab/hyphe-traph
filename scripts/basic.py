# -*- coding: utf-8 -*-
# =============================================================================
# Attempts Script
# =============================================================================
#
# Trying to make this whole thing work...
#
from traph import Traph
from scripts.utils.webentity_store import WebEntityStore

# Constants
PAGES = [
    's:http|h:fr|h:sciences-po|h:medialab|',
    's:https|h:com|h:twitter|p:paulanomalie|',
    's:https|h:192.168.0.1|p:paulanomalie|',
    's:http|h:com|h:twitter|p:papa|',
    's:http|h:com|h:twitter|p:pépé|',
    's:http|h:com|h:twitter|p:pépé|today|',
    's:http|h:com|h:twitter|p:pépé|yesterday|'
]

LINKS = [
    (0, 1),
    (0, 1),
    (0, 2),
    (1, 2),
    (1, 1)
]

webentity_creation_rules_regexp = {
    'domain':       '(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|))',
    'subdomain':    '(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)+|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|))',
    'path1':        '(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)+|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|)(p:[^\\|]+\\|){1})',
    'path2':        '(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)+|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|)(p:[^\\|]+\\|){2})'
}

webentity_default_creation_rule = webentity_creation_rules_regexp['domain']

webentity_creation_rules = {
    's:http|h:com|h:twitter|': webentity_creation_rules_regexp['path1'],
    's:http|h:com|h:facebook|': webentity_creation_rules_regexp['path1'],
    's:http|h:com|h:linkedin|': webentity_creation_rules_regexp['path2']
}

webentity_store = WebEntityStore('./scripts/data/webentities.json')

# Truncating the file for our purpose
lru_trie_file = open('./scripts/data/lru_trie.dat', 'wb+')
link_store_file = open('./scripts/data/link_store.dat', 'wb+')

traph = Traph(lru_trie_file=lru_trie_file, link_store_file=link_store_file,
              webentity_default_creation_rule=webentity_default_creation_rule,
              webentity_creation_rules=webentity_creation_rules)
trie = traph.lru_trie
links = traph.link_store

for page in PAGES:
    traph.add_page(page)

for page in trie.pages_iter():
    print page

for source, target in LINKS:
    source_node = trie.lru_node(PAGES[source])
    target_node = trie.lru_node(PAGES[target])

    links.add_link(source_node, target_node.block)

for source_page in PAGES:
    source_node = trie.lru_node(source_page)

    if not source_node.has_outlinks():
        continue

    for link_node in links.link_nodes_iter(source_node.outlinks()):
        print source_node, link_node

# Cleanup
lru_trie_file.close()
link_store_file.close()
