# =============================================================================
# Debug Script
# =============================================================================
#
# Reading information from an already existing Traph.
#
from traph import Traph

# Reading the file for our purpose
lruTrieFile = open('./scripts/data/lru_trie.dat', 'rb')

traph = Traph(lru_trie_file=lruTrieFile)
trie = traph.lru_trie

count = 0

for page in trie.pages_iter():
    count += 1

print count

lruTrieFile.close()
