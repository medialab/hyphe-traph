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
    's:https|h:192.168.0.1|p:paulanomalie|'
]

LINKS = [
    (0, 1),
    (0, 1),
    (0, 2),
    (1, 2),
    (1, 1)
]

webentity_store = WebEntityStore('./scripts/data/webentities.json')

# Truncating the file for our purpose
lru_trie_file = open('./scripts/data/lru_trie.dat', 'wb+')
link_store_file = open('./scripts/data/link_store.dat', 'wb+')

traph = Traph(lru_trie_file=lru_trie_file, link_store_file=link_store_file)
trie = traph.lru_trie
links = traph.link_store

for page in PAGES:
    traph.add_page(page)

for page in trie.pages_iter():
    print page

for source, target in LINKS:
    source_node = trie.lru_node(PAGES[source])
    target_node = trie.lru_node(PAGES[target])

    if not source_node.has_outlinks():
        block = links.add_first_link(target_node.block)
        source_node.set_outlinks(block)
        source_node.write()
    else:
        links.add_link(source_node.outlinks(), target_node.block)

for source_page in PAGES:
    source_node = trie.lru_node(source_page)

    for link_node in links.link_nodes_iter(source_node.outlinks()):
        print source_node, link_node

# Cleanup
lru_trie_file.close()
link_store_file.close()
