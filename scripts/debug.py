# =============================================================================
# Debug Script
# =============================================================================
#
# Reading information from an already existing Traph.
#
import os
from traph import Traph

# Creating data folder
if not os.path.isdir('./scripts/data'):
    os.makedirs('./scripts/data')

# Reading the file for our purpose
lruTrieFile = open('./scripts/data/lru_trie.dat', 'rb')

traph = Traph(lru_trie_file=lruTrieFile)
trie = traph.lru_trie

print len(list(trie.pages_iter()))

lruTrieFile.close()
