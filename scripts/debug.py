# =============================================================================
# Debug Script
# =============================================================================
#
# Reading information from an already existing Traph.
#
from traph import Traph

# Reading the file for our purpose
lru_trie_file = open('./scripts/data/lru_trie.dat', 'rb')
link_store_file = open('./scripts/data/link_store.dat', 'rb')

traph = Traph(lru_trie_file=lru_trie_file, link_store_file=link_store_file)
trie = traph.lru_trie
links = traph.link_store

# count = 0

# for page in trie.pages_iter():
#     count += 1

# print count

for page in trie.pages_iter():
    print page

lru_trie_file.close()
link_store_file.close()
