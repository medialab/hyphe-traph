# =============================================================================
# Unit Tests Helpers
# =============================================================================
#
# Miscellaneous helper functions used by the unit tests.
#
from collections import defaultdict


def webentity_label_from_prefixes(prefixes):
    for prefix in prefixes:
        if prefix.startswith('s:http|') and 'www' not in prefix:
            return prefix

    raise Exception('Could not find a fitting prefix.')


def legible_network(webentities, network):
    new_network = defaultdict(list)

    for source, targets in network.items():
        new_network[webentities[source]] = [webentities[target] for target in targets if target not in ['pages_crawled', 'pages_uncrawled']]
        if not new_network[webentities[source]]:
            del new_network[webentities[source]]

    return new_network
