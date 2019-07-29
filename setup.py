from setuptools import setup
from os import path

__version__ = None
here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'traph', 'version.py')) as version:
    exec(version.read())
assert __version__ is not None

setup(name='hyphe-traph',
      version=__version__,
      description='A Trie/Graph hybrid memory structure used by the Hyphe crawler to index pages & webentities.',
      url='http://github.com/medialab/hyphe-traph',
      license='MIT',
      author='Guillaume Plique',
      packages=[
        'traph',
        'traph.link_store',
        'traph.lru_trie',
        'traph.storage'
      ],
      zip_safe=True)
