# -*- coding: utf-8 -*-
# =============================================================================
# Attempts Script
# =============================================================================
#
# Trying to make this whole thing work...
#
import networkx as nx
from traph import Traph
from scripts.utils.webentity_store import WebEntityStore

# Constants
PAGES = [
    "s:http|h:fr|h:sciences-po|h:medialab|",
    "s:https|h:com|h:twitter|p:paulanomalie|",
    "s:https|h:192.168.0.1|p:paulanomalie|",
    "s:http|h:com|h:twitter|p:papa|",
    "s:http|h:com|h:twitter|p:pépé|",
    "s:http|h:com|h:twitter|p:pépé|today|",
    "s:http|h:com|h:twitter|p:pépé|yesterday|",
]

LINKS = [
    [
        "s:http|h:fr|h:sciences-po|h:medialab|",
        "s:https|h:com|h:twitter|p:paulanomalie|",
    ],
    ["s:http|h:com|h:twitter|p:papa|", "s:http|h:com|h:twitter|p:pépé|"],
    ["s:http|h:com|h:twitter|p:papa|", "s:http|h:com|h:twitter|p:mémé|"],
]

webentity_creation_rules_regexp = {
    "domain": "(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|))",
    "subdomain": "(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)+|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|))",
    "path1": "(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)+|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|)(p:[^\\|]+\\|){1})",
    "path2": "(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)+|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|)(p:[^\\|]+\\|){2})",
}

default_webentity_creation_rule = webentity_creation_rules_regexp["domain"]

webentity_creation_rules = {
    "s:http|h:com|h:twitter|": webentity_creation_rules_regexp["path1"],
    "s:http|h:com|h:facebook|": webentity_creation_rules_regexp["path1"],
    "s:http|h:com|h:linkedin|": webentity_creation_rules_regexp["path2"],
}

webentity_store = WebEntityStore("./scripts/data/webentities.json")

traph = Traph(
    overwrite=True,
    folder="./scripts/data/",
    default_webentity_creation_rule=default_webentity_creation_rule,
    webentity_creation_rules=webentity_creation_rules,
)
trie = traph.lru_trie
links = traph.link_store

print(trie.header)
print(links.header)


for page in PAGES:
    traph.add_page(page)

traph.add_links(LINKS)

for source_lru, target_lru in traph.links_iter():
    print("Source: %s, Target: %s" % (source_lru, target_lru))

for node in links.nodes_iter():
    print(node)

print("\nDetailed DFS...")
g = nx.Graph()
for state in trie.detailed_dfs_iter():
    print(state)

    g.add_node(state.node.block, label=state.node.char_as_str())

    if state.node.is_root():
        g.node[state.node.block]["viz"] = {"color": {"r": 255, "g": 0, "b": 0}}

    if not state.node.is_root():
        g.add_edge(state.node.parent(), state.node.block)

print("\nRepresentation:")
print(trie.representation())

# nx.write_gexf(g, './scripts/data/dump.gexf')

traph.close()
