# =============================================================================
# Unit Tests Config
# =============================================================================
#
# Gathering some default config that the unit tests files will use to create
# their traphs.
#
WEBENTITY_CREATION_RULES_REGEXES = {
    "domain": b"(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|))",
    "subdomain": b"(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)+|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|))",
    "path1": b"(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)+|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|)(p:[^\\|]+\\|){1})",
    "path2": b"(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)+|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|)(p:[^\\|]+\\|){2})",
    "path3": b"(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)+|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|)(p:[^\\|]+\\|){3})",
    "path4": b"(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)+|h:(localhost|(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|)(p:[^\\|]+\\|){4})",
}

DEFAULT_WEBENTITY_CREATION_RULE = WEBENTITY_CREATION_RULES_REGEXES["domain"]

WEBENTITY_CREATION_RULES = {
    b"s:http|h:com|h:twitter|": WEBENTITY_CREATION_RULES_REGEXES["path1"],
    b"s:http|h:com|h:facebook|": WEBENTITY_CREATION_RULES_REGEXES["path1"],
    b"s:http|h:com|h:linkedin|": WEBENTITY_CREATION_RULES_REGEXES["path2"],
}
