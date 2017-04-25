# =============================================================================
# Attempts Script
# =============================================================================
#
# Trying to make this whole thing work...
#
import os
from traph import Traph

# Constants
PAGES = [
    's:http|h:fr|h:sciences-po|h:medialab|',
    's:https|h:com|h:twitter|p:paulanomalie|',
    's:https|h:192.168.0.1|p:paulanomalie|'
]

# Creating data folder
if not os.path.isdir('./scripts/data'):
    os.makedirs('./scripts/data')

# Truncating the file for our purpose
lruTrieFile = open('./scripts/data/lru_trie.dat', 'wb+')

traph = Traph(lru_trie_file=lruTrieFile)

for page in PAGES:
    traph.add_page(page)

for page in traph.lru_trie.pages_iter():
    print page

lruTrieFile.close()
