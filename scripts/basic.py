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
    ['s:http|h:fr|h:sciences-po|h:medialab|', 's:https|h:com|h:twitter|p:paulanomalie|'],
    ['s:http|h:com|h:twitter|p:papa|', 's:http|h:com|h:twitter|p:pépé|'],
    ['s:http|h:com|h:twitter|p:papa|', 's:http|h:com|h:twitter|p:mémé|']
]

webentity_creation_rules_regexp = {
    'domain':       '(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|))',
    'subdomain':    '(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)+|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|))',
    'path1':        '(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)+|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|)(p:[^\\|]+\\|){1})',
    'path2':        '(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)+|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|)(p:[^\\|]+\\|){2})'
}

default_webentity_creation_rule = webentity_creation_rules_regexp['domain']

webentity_creation_rules = {
    's:http|h:com|h:twitter|': webentity_creation_rules_regexp['path1'],
    's:http|h:com|h:facebook|': webentity_creation_rules_regexp['path1'],
    's:http|h:com|h:linkedin|': webentity_creation_rules_regexp['path2']
}

webentity_store = WebEntityStore('./scripts/data/webentities.json')

traph = Traph(create=True, folder='./scripts/data/',
              default_webentity_creation_rule=default_webentity_creation_rule,
              webentity_creation_rules=webentity_creation_rules)
trie = traph.lru_trie
links = traph.link_store

print trie.header
print links.header


for page in PAGES:
    traph.add_page(page)

traph.add_links(LINKS)

for node, lru in trie.pages_iter():
    print lru

# for node in trie.nodes_iter():
#     if node.webentity():
#         print node

# for source, target in LINKS:
#     source_node = trie.lru_node(PAGES[source])
#     target_node = trie.lru_node(PAGES[target])

#     links.add_link(source_node, target_node.block)

# for source_page in PAGES:
#     source_node = trie.lru_node(source_page)

#     if not source_node.has_outlinks():
#         continue

#     for link_node in links.link_nodes_iter(source_node.outlinks()):
#         print source_node, link_node

# for node in trie.nodes_iter():
#     if node.webentity():
#         print node

traph.close()
