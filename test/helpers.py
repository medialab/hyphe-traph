# =============================================================================
# Unit Tests Helpers
# =============================================================================
#
# Miscellaneous helper functions used by the unit tests.
#


def webentity_label_from_prefixes(prefixes):
    for prefix in prefixes:
        if prefix.startswith('s:http|') and 'www' not in prefix:
            return prefix

    raise Exception('Could not find a fitting prefix.')
