# Abstract FOSDEM 2018

**It's a Trie... it's a Graph... it's a Traph!**

*Designing an on-file multi-level graph index for the Hyphe web crawler*

Hyphe, a social sciences-oriented web crawler developed by SciencesPo's médialab, introduced the novel concept of web entities to represent the very subjective nature of web pages' aggregation into meaningful groupings. This, however, does not come without technical challenges since indexing the dynamic graph of web entities lying above the web pages' one is not as straightforward as it may naively seems.

Our intent is therefore to present the graph community with our feedback about the design of an on-file index - part Graph, part Trie - named the "Traph", to solve this peculiar use-case. What's more, we propose to walk you through the path we followed from an old Lucene index, to our experiments with Neo4j and lastly our conclusions that we needed to develop our own data structure to be able to scale correctly.

## Speakers

* Paul Girard
* Matthieu Jacomy
* Benjamin Ooghe-Tabanou
* Guillaume Plique

## Links

* [Hyphe](http://hyphe.medialab.sciences-po.fr/)
* [The Traph sources](https://github.com/medialab/hyphe-traph)
* [SciencesPo's médialab](http://www.medialab.sciences-po.fr/)

