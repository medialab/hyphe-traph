# -*- coding: utf-8 -*-
# =============================================================================
# Attempts Script
# =============================================================================
#
# Trying to make this whole thing work...
#
from traph import Traph

webentity_creation_rules_regexp = {
    "domain": "(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|))",
    "subdomain": "(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)+|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|))",
    "path1": "(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)+|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|)(p:[^\\|]+\\|){1})",
    "path2": "(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)+|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|)(p:[^\\|]+\\|){2})",
}

default_webentity_creation_rule = webentity_creation_rules_regexp["domain"]

webentity_creation_rules = {
    "s:http|h:com|h:twitter|": webentity_creation_rules_regexp["path1"],
}

# Creating the Traph
traph = Traph(
    folder="./scripts/data/",
    default_webentity_creation_rule=default_webentity_creation_rule,
    webentity_creation_rules=webentity_creation_rules,
)

# webentities_network = traph.get_webentities_links()
from pprint import pprint

metrics = traph.lru_trie.metrics()

pprint(metrics)
# g = nx.Graph()

# for source, targets in webentities_network.items():
#     g.add_node(source, label=source)

#     for target in targets:
#         g.add_node(target, label=target)
#         g.add_edge(source, target)

# nx.write_gexf(g, './scripts/data/dump.gexf')
