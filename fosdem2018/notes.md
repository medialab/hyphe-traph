# Notes

# Plan proposition

1. Hyphe & background (web entities, LRUs, stems etc.)
2. The Lucene structure
3. Our gambit to create a better index
4. The neo4j experience
5. Designing the on-file index (check history of the structure)
6. Consequences & the future

## Miscellaneaous

* Check the history of the structure for insight.
* `UNWIND` is your friend.
* Neo4j stored procedures.
* No need for deletion, no need for ACID, just an on-file index. This means that the index stores no "original" data and can be recomputed from data stored in a legitimate database (MongoDB) in our case.
* Humility => ask for insights on the structure so we can better it further.
