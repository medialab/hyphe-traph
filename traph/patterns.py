# =============================================================================
# WebEntity Creation Rules Patterns
# =============================================================================
#
# Gathering main webentity creation rules pattern.
#
import re

DEFAULT = re.compile(
    '(s:[a-zA-Z]+\\|(t:[0-9]+\\|)?(h:[^\\|]+\\|(h:[^\\|]+\\|)|h:(localhost|'
    '(\\d{1,3}\\.){3}\\d{1,3}|\\[[\\da-f]*:[\\da-f:]*\\])\\|))'
)
