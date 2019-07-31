# Pagination

## In order page pagination tokens

To be able to resume a webentity in order page pagination we output a token consisting of the following parts:

1. The webentity current prefix index
2. The block of the last yielded page
3. The path from the prefix to the last yielded page encoded as base64 & representing a base4 path where:
   1. `1` is the left path
   2. `2` is the middle path
   3. `3` is the right path
