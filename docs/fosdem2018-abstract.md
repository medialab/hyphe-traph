# Abstract FOSDEM 2018

**It's a Trie... it's a Graph... it's a Traph!**

*Designing an on-file multi-level graph index for the Hyphe web crawler*

Hyphe, a social sciences-oriented web crawler developed by the SciencesPo médialab, introduced the novel concept of web entities to provide a flexible way of grouping web pages in situations where the notion of website is not relevant enough (Twitter accounts, newspaper articles...). This comes with technical challenges since indexing a graph of web entities as a dynamic layer based on a large number of URLs is not as straightforward as it may seem.

We aim at providing the graph community with some feedback about the design of an on-file index - part Graph, part Trie - named the "Traph", to solve this peculiar use-case. Additionally we propose to retrace the path we followed, from an old Lucene index, to our experiments with Neo4j, and lastly to our conclusion that we needed to develop our own data structure in order to be able to scale up.

## Speakers

* Paul Girard
* Mathieu Jacomy
* Benjamin Ooghe-Tabanou
* Guillaume Plique

## Links

* [Hyphe](http://hyphe.medialab.sciences-po.fr/)
* [The Traph sources](https://github.com/medialab/hyphe-traph)
* [Hyphe's paper at the 10th International AAAI Conference on Web and Social Media (ICWSM-16)](https://www.aaai.org/ocs/index.php/ICWSM/ICWSM16/paper/download/13051/12797)
* [SciencesPo's médialab](http://www.medialab.sciences-po.fr/)

