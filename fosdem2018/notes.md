# Notes

# Plan proposition

1. Hyphe & background (web entities, LRUs, stems, creation rules etc.)
2. The Lucene structure
3. The problem: "not" queries
4. Our gambit to create a better index
5. The neo4j experience
6. Traph wins
7. Designing the on-file index (check history of the structure)
8. Consequences & the future

## Miscellaneaous

* Check the history of the structure for insight.
* `UNWIND` is your friend.
* Neo4j stored procedures.
* No need for deletion, no need for ACID, just an on-file index. This means that the index stores no "original" data and can be recomputed from data stored in a legitimate database (MongoDB) in our case.
* linked to previous: fear for "from scratch" data structure, tradeoff specific salty blast vs. generic sugary slower
* Humility => ask for insights on the structure so we can better it further.
* humility => Lucene started with a bad subcontractor
