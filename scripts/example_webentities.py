# -*- coding: utf-8 -*-
# =============================================================================
# Example metaphor: famous websites
# =============================================================================
#
# - No links in this example
#
from traph import Traph
from scripts.utils.webentity_store import WebEntityStore

webentity_creation_rules_regexp = {
    "domain": "(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|))",
    "subdomain": "(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)+|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|))",
    "path1": "(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)+|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|)(p:[^\\|]+\\|){1})",
    "path2": "(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)+|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|)(p:[^\\|]+\\|){2})",
}

default_webentity_creation_rule = webentity_creation_rules_regexp["domain"]

webentity_creation_rules = {}

# Webentity store is necessary to keep track of web entities' prefixes.
# Though the traph could retrieve them, it would not be efficient.
# In a real situation, these would be tracked elsewhere.
# That's what we are simulating with this store.
webentity_store = WebEntityStore("./scripts/data/webentities.json")
webentity_store.data["webentities"] = {}

# Instanciate the traph
traph = Traph(
    overwrite=True,
    folder="./scripts/data/",
    default_webentity_creation_rule=default_webentity_creation_rule,
    webentity_creation_rules=webentity_creation_rules,
)

# Step 1
print(
    '\n:: Step 1 - Create a "Boeing" webentity with the 4 prefix variations (WWW and HTTPS cases).'
)
print("Expected: Creates the entity with the 4 prefixes. This is the typical use case.")

boeing_prefixes = [
    "s:http|h:com|h:boeing|",
    "s:http|h:com|h:boeing|h:www|",
    "s:https|h:com|h:boeing|",
    "s:https|h:com|h:boeing|h:www|",
]
report = traph.create_webentity(boeing_prefixes)
webentity_store.data["webentities"].update(report.created_webentities)
boeing_weid = list(report.created_webentities.keys())[0]  # Used for a step below

print("\nResult - Existing webentities from Store:")
for weid, prefixes in list(webentity_store.data["webentities"].items()):
    print(" - Webentity %s:" % (weid))
    for prefix in prefixes:
        print("\t\t" + prefix)

print("\nResult - Prefixes from Traph:")
for node, lru in traph.webentity_prefix_iter():
    print(" - (%s) \t%s" % (node.webentity(), lru))


# Step 2
print(
    '\n:: Step 2 - Create a "Airbus HTTPS" webentity with only 2 prefix variations (WWW case).'
)
print("Expected: Creates the entity with the 2 prefixes.")

airbus_prefixes = ["s:https|h:com|h:airbus|", "s:https|h:com|h:airbus|h:www|"]
report = traph.create_webentity(airbus_prefixes)
webentity_store.data["webentities"].update(report.created_webentities)

print("\nResult - Existing webentities from Store:")
for weid, prefixes in list(webentity_store.data["webentities"].items()):
    print(" - Webentity %s:" % (weid))
    for prefix in prefixes:
        print("\t\t" + prefix)

print("\nResult - Prefixes from Traph:")
for node, lru in traph.webentity_prefix_iter():
    print(" - (%s) \t%s" % (node.webentity(), lru))


# Step 3
print('\n:: Step 3 - Remove the "Boeing" webentity')
print("Expected: Only Airbus remains")

traph.delete_webentity(boeing_weid, webentity_store.data["webentities"][boeing_weid])
del webentity_store.data["webentities"][boeing_weid]

print("\nResult - Existing webentities from Store:")
for weid, prefixes in list(webentity_store.data["webentities"].items()):
    print(" - Webentity %s:" % (weid))
    for prefix in prefixes:
        print("\t\t" + prefix)

print("\nResult - Prefixes from Traph:")
for node, lru in traph.webentity_prefix_iter():
    print(" - (%s) \t%s" % (node.webentity(), lru))


# Step 4
print('\n:: Step 4 - Add the "Airbus/blog" page')
print("Expected: Create the NON-HTTPS Airbus webentity")

report = traph.add_page("s:http|h:com|h:airbus|p:blog|")
webentity_store.data["webentities"].update(report.created_webentities)

print("\nResult - Existing webentities from Store:")
for weid, prefixes in list(webentity_store.data["webentities"].items()):
    print(" - Webentity %s:" % (weid))
    for prefix in prefixes:
        print("\t\t" + prefix)

print("\nResult - Prefixes from Traph:")
for node, lru in traph.webentity_prefix_iter():
    print(" - (%s) \t%s" % (node.webentity(), lru))

print(
    "\nResult - Airbus blog page belongs to webentity %s via prefix %s"
    % (
        traph.retrieve_webentity("s:http|h:com|h:airbus|p:blog|"),
        traph.retrieve_prefix("s:http|h:com|h:airbus|p:blog|"),
    )
)


# Step 5
print("\n:: Step 5 - Move the NON-HTTPS prefixes to the HTTPS Airbus entity")
print("Expected: A single Airbus webentity")

prefixes = ["s:http|h:com|h:airbus|", "s:http|h:com|h:airbus|h:www|"]
for prefix in prefixes:
    if traph.move_prefix_to_webentity(prefix, 2):
        # Remove from source webentity in store
        store_prefixes = webentity_store.data["webentities"][3]
        store_prefixes.remove(prefix)
        webentity_store.data["webentities"].update({3: store_prefixes})

        if len(store_prefixes) == 0:
            del webentity_store.data["webentities"][3]

        # Add to target webentity in store
        store_prefixes = webentity_store.data["webentities"][2]
        store_prefixes.append(prefix)
        webentity_store.data["webentities"].update({2: store_prefixes})

print("\nResult - Existing webentities from Store:")
for weid, prefixes in list(webentity_store.data["webentities"].items()):
    print(" - Webentity %s:" % (weid))
    for prefix in prefixes:
        print("\t\t" + prefix)

print("\nResult - Prefixes from Traph:")
for node, lru in traph.webentity_prefix_iter():
    print(" - (%s) \t%s" % (node.webentity(), lru))

print(
    "\nResult - Airbus blog page belongs to webentity %s via prefix %s"
    % (
        traph.retrieve_webentity("s:http|h:com|h:airbus|p:blog|"),
        traph.retrieve_prefix("s:http|h:com|h:airbus|p:blog|"),
    )
)


traph.close()
