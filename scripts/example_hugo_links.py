# -*- coding: utf-8 -*-
# =============================================================================
# Example metaphor: characters of Les Misérables, from the famous network
# =============================================================================
#
from traph import Traph
from scripts.utils.webentity_store import WebEntityStore

# Constants
PAGES = [
    "s:http|h:com|h:myriel|",
    "s:http|h:com|h:napoleon|",
    "s:http|h:com|h:mllebaptistine|",
    "s:http|h:com|h:mmemagloire|",
    "s:http|h:com|h:countessdelo|",
    "s:http|h:com|h:geborand|",
    "s:http|h:com|h:champtercier|",
    "s:http|h:com|h:cravatte|",
    "s:http|h:com|h:count|",
    "s:http|h:com|h:oldman|",
    "s:http|h:com|h:labarre|",
    "s:http|h:com|h:valjean|",
    "s:http|h:com|h:marguerite|",
    "s:http|h:com|h:mmeder|",
    "s:http|h:com|h:isabeau|",
    "s:http|h:com|h:gervais|",
    "s:http|h:com|h:tholomyes|",
    "s:http|h:com|h:listolier|",
    "s:http|h:com|h:fameuil|",
    "s:http|h:com|h:blacheville|",
    "s:http|h:com|h:favourite|",
    "s:http|h:com|h:dahlia|",
    "s:http|h:com|h:zephine|",
    "s:http|h:com|h:fantine|",
    "s:http|h:com|h:mmethenardier|",
    "s:http|h:com|h:thenardier|",
    "s:http|h:com|h:cosette|",
    "s:http|h:com|h:javert|",
    "s:http|h:com|h:fauchelevent|",
    "s:http|h:com|h:bamatabois|",
    "s:http|h:com|h:perpetue|",
    "s:http|h:com|h:simplice|",
    "s:http|h:com|h:scaufflaire|",
    "s:http|h:com|h:woman1|",
    "s:http|h:com|h:judge|",
    "s:http|h:com|h:champmathieu|",
    "s:http|h:com|h:brevet|",
    "s:http|h:com|h:chenildieu|",
    "s:http|h:com|h:cochepaille|",
    "s:http|h:com|h:pontmercy|",
    "s:http|h:com|h:boulatruelle|",
    "s:http|h:com|h:eponine|",
    "s:http|h:com|h:anzelma|",
    "s:http|h:com|h:woman2|",
    "s:http|h:com|h:motherinnocent|",
    "s:http|h:com|h:gribier|",
    "s:http|h:com|h:jondrette|",
    "s:http|h:com|h:mmeburgon|",
    "s:http|h:com|h:gavroche|",
    "s:http|h:com|h:gillenormand|",
    "s:http|h:com|h:magnon|",
    "s:http|h:com|h:mllegillenormand|",
    "s:http|h:com|h:mmepontmercy|",
    "s:http|h:com|h:mllevaubois|",
    "s:http|h:com|h:ltgillenormand|",
    "s:http|h:com|h:marius|",
    "s:http|h:com|h:baronesst|",
    "s:http|h:com|h:mabeuf|",
    "s:http|h:com|h:enjolras|",
    "s:http|h:com|h:combeferre|",
    "s:http|h:com|h:prouvaire|",
    "s:http|h:com|h:feuilly|",
    "s:http|h:com|h:courfeyrac|",
    "s:http|h:com|h:bahorel|",
    "s:http|h:com|h:bossuet|",
    "s:http|h:com|h:joly|",
    "s:http|h:com|h:grantaire|",
    "s:http|h:com|h:motherplutarch|",
    "s:http|h:com|h:gueulemer|",
    "s:http|h:com|h:babet|",
    "s:http|h:com|h:claquesous|",
    "s:http|h:com|h:montparnasse|",
    "s:http|h:com|h:toussaint|",
    "s:http|h:com|h:child1|",
    "s:http|h:com|h:child2|",
    "s:http|h:com|h:brujon|",
    "s:http|h:com|h:mmehucheloup|",
]

LINKS = [
    ["s:http|h:com|h:napoleon|", "s:http|h:com|h:myriel|"],
    ["s:http|h:com|h:mllebaptistine|", "s:http|h:com|h:myriel|"],
    ["s:http|h:com|h:mmemagloire|", "s:http|h:com|h:myriel|"],
    ["s:http|h:com|h:mmemagloire|", "s:http|h:com|h:mllebaptistine|"],
    ["s:http|h:com|h:countessdelo|", "s:http|h:com|h:myriel|"],
    ["s:http|h:com|h:geborand|", "s:http|h:com|h:myriel|"],
    ["s:http|h:com|h:champtercier|", "s:http|h:com|h:myriel|"],
    ["s:http|h:com|h:cravatte|", "s:http|h:com|h:myriel|"],
    ["s:http|h:com|h:count|", "s:http|h:com|h:myriel|"],
    ["s:http|h:com|h:oldman|", "s:http|h:com|h:myriel|"],
    ["s:http|h:com|h:valjean|", "s:http|h:com|h:myriel|"],
    ["s:http|h:com|h:valjean|", "s:http|h:com|h:mllebaptistine|"],
    ["s:http|h:com|h:valjean|", "s:http|h:com|h:mmemagloire|"],
    ["s:http|h:com|h:valjean|", "s:http|h:com|h:labarre|"],
    ["s:http|h:com|h:marguerite|", "s:http|h:com|h:valjean|"],
    ["s:http|h:com|h:mmeder|", "s:http|h:com|h:valjean|"],
    ["s:http|h:com|h:isabeau|", "s:http|h:com|h:valjean|"],
    ["s:http|h:com|h:gervais|", "s:http|h:com|h:valjean|"],
    ["s:http|h:com|h:listolier|", "s:http|h:com|h:tholomyes|"],
    ["s:http|h:com|h:fameuil|", "s:http|h:com|h:tholomyes|"],
    ["s:http|h:com|h:fameuil|", "s:http|h:com|h:listolier|"],
    ["s:http|h:com|h:blacheville|", "s:http|h:com|h:tholomyes|"],
    ["s:http|h:com|h:blacheville|", "s:http|h:com|h:listolier|"],
    ["s:http|h:com|h:blacheville|", "s:http|h:com|h:fameuil|"],
    ["s:http|h:com|h:favourite|", "s:http|h:com|h:tholomyes|"],
    ["s:http|h:com|h:favourite|", "s:http|h:com|h:listolier|"],
    ["s:http|h:com|h:favourite|", "s:http|h:com|h:fameuil|"],
    ["s:http|h:com|h:favourite|", "s:http|h:com|h:blacheville|"],
    ["s:http|h:com|h:dahlia|", "s:http|h:com|h:tholomyes|"],
    ["s:http|h:com|h:dahlia|", "s:http|h:com|h:listolier|"],
    ["s:http|h:com|h:dahlia|", "s:http|h:com|h:fameuil|"],
    ["s:http|h:com|h:dahlia|", "s:http|h:com|h:blacheville|"],
    ["s:http|h:com|h:dahlia|", "s:http|h:com|h:favourite|"],
    ["s:http|h:com|h:zephine|", "s:http|h:com|h:tholomyes|"],
    ["s:http|h:com|h:zephine|", "s:http|h:com|h:listolier|"],
    ["s:http|h:com|h:zephine|", "s:http|h:com|h:fameuil|"],
    ["s:http|h:com|h:zephine|", "s:http|h:com|h:blacheville|"],
    ["s:http|h:com|h:zephine|", "s:http|h:com|h:favourite|"],
    ["s:http|h:com|h:zephine|", "s:http|h:com|h:dahlia|"],
    ["s:http|h:com|h:fantine|", "s:http|h:com|h:valjean|"],
    ["s:http|h:com|h:fantine|", "s:http|h:com|h:marguerite|"],
    ["s:http|h:com|h:fantine|", "s:http|h:com|h:tholomyes|"],
    ["s:http|h:com|h:fantine|", "s:http|h:com|h:listolier|"],
    ["s:http|h:com|h:fantine|", "s:http|h:com|h:fameuil|"],
    ["s:http|h:com|h:fantine|", "s:http|h:com|h:blacheville|"],
    ["s:http|h:com|h:fantine|", "s:http|h:com|h:favourite|"],
    ["s:http|h:com|h:fantine|", "s:http|h:com|h:dahlia|"],
    ["s:http|h:com|h:fantine|", "s:http|h:com|h:zephine|"],
    ["s:http|h:com|h:mmethenardier|", "s:http|h:com|h:valjean|"],
    ["s:http|h:com|h:mmethenardier|", "s:http|h:com|h:fantine|"],
    ["s:http|h:com|h:thenardier|", "s:http|h:com|h:valjean|"],
    ["s:http|h:com|h:thenardier|", "s:http|h:com|h:fantine|"],
    ["s:http|h:com|h:thenardier|", "s:http|h:com|h:mmethenardier|"],
    ["s:http|h:com|h:cosette|", "s:http|h:com|h:valjean|"],
    ["s:http|h:com|h:cosette|", "s:http|h:com|h:tholomyes|"],
    ["s:http|h:com|h:cosette|", "s:http|h:com|h:mmethenardier|"],
    ["s:http|h:com|h:cosette|", "s:http|h:com|h:thenardier|"],
    ["s:http|h:com|h:javert|", "s:http|h:com|h:valjean|"],
    ["s:http|h:com|h:javert|", "s:http|h:com|h:fantine|"],
    ["s:http|h:com|h:javert|", "s:http|h:com|h:mmethenardier|"],
    ["s:http|h:com|h:javert|", "s:http|h:com|h:thenardier|"],
    ["s:http|h:com|h:javert|", "s:http|h:com|h:cosette|"],
    ["s:http|h:com|h:fauchelevent|", "s:http|h:com|h:valjean|"],
    ["s:http|h:com|h:fauchelevent|", "s:http|h:com|h:javert|"],
    ["s:http|h:com|h:bamatabois|", "s:http|h:com|h:valjean|"],
    ["s:http|h:com|h:bamatabois|", "s:http|h:com|h:fantine|"],
    ["s:http|h:com|h:bamatabois|", "s:http|h:com|h:javert|"],
    ["s:http|h:com|h:perpetue|", "s:http|h:com|h:fantine|"],
    ["s:http|h:com|h:simplice|", "s:http|h:com|h:valjean|"],
    ["s:http|h:com|h:simplice|", "s:http|h:com|h:fantine|"],
    ["s:http|h:com|h:simplice|", "s:http|h:com|h:javert|"],
    ["s:http|h:com|h:simplice|", "s:http|h:com|h:perpetue|"],
    ["s:http|h:com|h:scaufflaire|", "s:http|h:com|h:valjean|"],
    ["s:http|h:com|h:woman1|", "s:http|h:com|h:valjean|"],
    ["s:http|h:com|h:woman1|", "s:http|h:com|h:javert|"],
    ["s:http|h:com|h:judge|", "s:http|h:com|h:valjean|"],
    ["s:http|h:com|h:judge|", "s:http|h:com|h:bamatabois|"],
    ["s:http|h:com|h:champmathieu|", "s:http|h:com|h:valjean|"],
    ["s:http|h:com|h:champmathieu|", "s:http|h:com|h:bamatabois|"],
    ["s:http|h:com|h:champmathieu|", "s:http|h:com|h:judge|"],
    ["s:http|h:com|h:brevet|", "s:http|h:com|h:valjean|"],
    ["s:http|h:com|h:brevet|", "s:http|h:com|h:bamatabois|"],
    ["s:http|h:com|h:brevet|", "s:http|h:com|h:judge|"],
    ["s:http|h:com|h:brevet|", "s:http|h:com|h:champmathieu|"],
    ["s:http|h:com|h:chenildieu|", "s:http|h:com|h:valjean|"],
    ["s:http|h:com|h:chenildieu|", "s:http|h:com|h:bamatabois|"],
    ["s:http|h:com|h:chenildieu|", "s:http|h:com|h:judge|"],
    ["s:http|h:com|h:chenildieu|", "s:http|h:com|h:champmathieu|"],
    ["s:http|h:com|h:chenildieu|", "s:http|h:com|h:brevet|"],
    ["s:http|h:com|h:cochepaille|", "s:http|h:com|h:valjean|"],
    ["s:http|h:com|h:cochepaille|", "s:http|h:com|h:bamatabois|"],
    ["s:http|h:com|h:cochepaille|", "s:http|h:com|h:judge|"],
    ["s:http|h:com|h:cochepaille|", "s:http|h:com|h:champmathieu|"],
    ["s:http|h:com|h:cochepaille|", "s:http|h:com|h:brevet|"],
    ["s:http|h:com|h:cochepaille|", "s:http|h:com|h:chenildieu|"],
    ["s:http|h:com|h:pontmercy|", "s:http|h:com|h:thenardier|"],
    ["s:http|h:com|h:boulatruelle|", "s:http|h:com|h:thenardier|"],
    ["s:http|h:com|h:eponine|", "s:http|h:com|h:mmethenardier|"],
    ["s:http|h:com|h:eponine|", "s:http|h:com|h:thenardier|"],
    ["s:http|h:com|h:anzelma|", "s:http|h:com|h:mmethenardier|"],
    ["s:http|h:com|h:anzelma|", "s:http|h:com|h:thenardier|"],
    ["s:http|h:com|h:anzelma|", "s:http|h:com|h:eponine|"],
    ["s:http|h:com|h:woman2|", "s:http|h:com|h:valjean|"],
    ["s:http|h:com|h:woman2|", "s:http|h:com|h:cosette|"],
    ["s:http|h:com|h:woman2|", "s:http|h:com|h:javert|"],
    ["s:http|h:com|h:motherinnocent|", "s:http|h:com|h:valjean|"],
    ["s:http|h:com|h:motherinnocent|", "s:http|h:com|h:fauchelevent|"],
    ["s:http|h:com|h:gribier|", "s:http|h:com|h:fauchelevent|"],
    ["s:http|h:com|h:mmeburgon|", "s:http|h:com|h:jondrette|"],
    ["s:http|h:com|h:gavroche|", "s:http|h:com|h:valjean|"],
    ["s:http|h:com|h:gavroche|", "s:http|h:com|h:thenardier|"],
    ["s:http|h:com|h:gavroche|", "s:http|h:com|h:javert|"],
    ["s:http|h:com|h:gavroche|", "s:http|h:com|h:mmeburgon|"],
    ["s:http|h:com|h:gillenormand|", "s:http|h:com|h:valjean|"],
    ["s:http|h:com|h:gillenormand|", "s:http|h:com|h:cosette|"],
    ["s:http|h:com|h:magnon|", "s:http|h:com|h:mmethenardier|"],
    ["s:http|h:com|h:magnon|", "s:http|h:com|h:gillenormand|"],
    ["s:http|h:com|h:mllegillenormand|", "s:http|h:com|h:valjean|"],
    ["s:http|h:com|h:mllegillenormand|", "s:http|h:com|h:cosette|"],
    ["s:http|h:com|h:mllegillenormand|", "s:http|h:com|h:gillenormand|"],
    ["s:http|h:com|h:mmepontmercy|", "s:http|h:com|h:pontmercy|"],
    ["s:http|h:com|h:mmepontmercy|", "s:http|h:com|h:mllegillenormand|"],
    ["s:http|h:com|h:mllevaubois|", "s:http|h:com|h:mllegillenormand|"],
    ["s:http|h:com|h:ltgillenormand|", "s:http|h:com|h:cosette|"],
    ["s:http|h:com|h:ltgillenormand|", "s:http|h:com|h:gillenormand|"],
    ["s:http|h:com|h:ltgillenormand|", "s:http|h:com|h:mllegillenormand|"],
    ["s:http|h:com|h:marius|", "s:http|h:com|h:valjean|"],
    ["s:http|h:com|h:marius|", "s:http|h:com|h:tholomyes|"],
    ["s:http|h:com|h:marius|", "s:http|h:com|h:thenardier|"],
    ["s:http|h:com|h:marius|", "s:http|h:com|h:cosette|"],
    ["s:http|h:com|h:marius|", "s:http|h:com|h:pontmercy|"],
    ["s:http|h:com|h:marius|", "s:http|h:com|h:eponine|"],
    ["s:http|h:com|h:marius|", "s:http|h:com|h:gavroche|"],
    ["s:http|h:com|h:marius|", "s:http|h:com|h:gillenormand|"],
    ["s:http|h:com|h:marius|", "s:http|h:com|h:mllegillenormand|"],
    ["s:http|h:com|h:marius|", "s:http|h:com|h:ltgillenormand|"],
    ["s:http|h:com|h:baronesst|", "s:http|h:com|h:gillenormand|"],
    ["s:http|h:com|h:baronesst|", "s:http|h:com|h:marius|"],
    ["s:http|h:com|h:mabeuf|", "s:http|h:com|h:eponine|"],
    ["s:http|h:com|h:mabeuf|", "s:http|h:com|h:gavroche|"],
    ["s:http|h:com|h:mabeuf|", "s:http|h:com|h:marius|"],
    ["s:http|h:com|h:enjolras|", "s:http|h:com|h:valjean|"],
    ["s:http|h:com|h:enjolras|", "s:http|h:com|h:javert|"],
    ["s:http|h:com|h:enjolras|", "s:http|h:com|h:gavroche|"],
    ["s:http|h:com|h:enjolras|", "s:http|h:com|h:marius|"],
    ["s:http|h:com|h:enjolras|", "s:http|h:com|h:mabeuf|"],
    ["s:http|h:com|h:combeferre|", "s:http|h:com|h:gavroche|"],
    ["s:http|h:com|h:combeferre|", "s:http|h:com|h:marius|"],
    ["s:http|h:com|h:combeferre|", "s:http|h:com|h:mabeuf|"],
    ["s:http|h:com|h:combeferre|", "s:http|h:com|h:enjolras|"],
    ["s:http|h:com|h:prouvaire|", "s:http|h:com|h:gavroche|"],
    ["s:http|h:com|h:prouvaire|", "s:http|h:com|h:enjolras|"],
    ["s:http|h:com|h:prouvaire|", "s:http|h:com|h:combeferre|"],
    ["s:http|h:com|h:feuilly|", "s:http|h:com|h:gavroche|"],
    ["s:http|h:com|h:feuilly|", "s:http|h:com|h:marius|"],
    ["s:http|h:com|h:feuilly|", "s:http|h:com|h:mabeuf|"],
    ["s:http|h:com|h:feuilly|", "s:http|h:com|h:enjolras|"],
    ["s:http|h:com|h:feuilly|", "s:http|h:com|h:combeferre|"],
    ["s:http|h:com|h:feuilly|", "s:http|h:com|h:prouvaire|"],
    ["s:http|h:com|h:courfeyrac|", "s:http|h:com|h:eponine|"],
    ["s:http|h:com|h:courfeyrac|", "s:http|h:com|h:gavroche|"],
    ["s:http|h:com|h:courfeyrac|", "s:http|h:com|h:marius|"],
    ["s:http|h:com|h:courfeyrac|", "s:http|h:com|h:mabeuf|"],
    ["s:http|h:com|h:courfeyrac|", "s:http|h:com|h:enjolras|"],
    ["s:http|h:com|h:courfeyrac|", "s:http|h:com|h:combeferre|"],
    ["s:http|h:com|h:courfeyrac|", "s:http|h:com|h:prouvaire|"],
    ["s:http|h:com|h:courfeyrac|", "s:http|h:com|h:feuilly|"],
    ["s:http|h:com|h:bahorel|", "s:http|h:com|h:gavroche|"],
    ["s:http|h:com|h:bahorel|", "s:http|h:com|h:marius|"],
    ["s:http|h:com|h:bahorel|", "s:http|h:com|h:mabeuf|"],
    ["s:http|h:com|h:bahorel|", "s:http|h:com|h:enjolras|"],
    ["s:http|h:com|h:bahorel|", "s:http|h:com|h:combeferre|"],
    ["s:http|h:com|h:bahorel|", "s:http|h:com|h:prouvaire|"],
    ["s:http|h:com|h:bahorel|", "s:http|h:com|h:feuilly|"],
    ["s:http|h:com|h:bahorel|", "s:http|h:com|h:courfeyrac|"],
    ["s:http|h:com|h:bossuet|", "s:http|h:com|h:valjean|"],
    ["s:http|h:com|h:bossuet|", "s:http|h:com|h:gavroche|"],
    ["s:http|h:com|h:bossuet|", "s:http|h:com|h:marius|"],
    ["s:http|h:com|h:bossuet|", "s:http|h:com|h:mabeuf|"],
    ["s:http|h:com|h:bossuet|", "s:http|h:com|h:enjolras|"],
    ["s:http|h:com|h:bossuet|", "s:http|h:com|h:combeferre|"],
    ["s:http|h:com|h:bossuet|", "s:http|h:com|h:prouvaire|"],
    ["s:http|h:com|h:bossuet|", "s:http|h:com|h:feuilly|"],
    ["s:http|h:com|h:bossuet|", "s:http|h:com|h:courfeyrac|"],
    ["s:http|h:com|h:bossuet|", "s:http|h:com|h:bahorel|"],
    ["s:http|h:com|h:joly|", "s:http|h:com|h:gavroche|"],
    ["s:http|h:com|h:joly|", "s:http|h:com|h:marius|"],
    ["s:http|h:com|h:joly|", "s:http|h:com|h:mabeuf|"],
    ["s:http|h:com|h:joly|", "s:http|h:com|h:enjolras|"],
    ["s:http|h:com|h:joly|", "s:http|h:com|h:combeferre|"],
    ["s:http|h:com|h:joly|", "s:http|h:com|h:prouvaire|"],
    ["s:http|h:com|h:joly|", "s:http|h:com|h:feuilly|"],
    ["s:http|h:com|h:joly|", "s:http|h:com|h:courfeyrac|"],
    ["s:http|h:com|h:joly|", "s:http|h:com|h:bahorel|"],
    ["s:http|h:com|h:joly|", "s:http|h:com|h:bossuet|"],
    ["s:http|h:com|h:grantaire|", "s:http|h:com|h:gavroche|"],
    ["s:http|h:com|h:grantaire|", "s:http|h:com|h:enjolras|"],
    ["s:http|h:com|h:grantaire|", "s:http|h:com|h:combeferre|"],
    ["s:http|h:com|h:grantaire|", "s:http|h:com|h:prouvaire|"],
    ["s:http|h:com|h:grantaire|", "s:http|h:com|h:feuilly|"],
    ["s:http|h:com|h:grantaire|", "s:http|h:com|h:courfeyrac|"],
    ["s:http|h:com|h:grantaire|", "s:http|h:com|h:bahorel|"],
    ["s:http|h:com|h:grantaire|", "s:http|h:com|h:bossuet|"],
    ["s:http|h:com|h:grantaire|", "s:http|h:com|h:joly|"],
    ["s:http|h:com|h:motherplutarch|", "s:http|h:com|h:mabeuf|"],
    ["s:http|h:com|h:gueulemer|", "s:http|h:com|h:valjean|"],
    ["s:http|h:com|h:gueulemer|", "s:http|h:com|h:mmethenardier|"],
    ["s:http|h:com|h:gueulemer|", "s:http|h:com|h:thenardier|"],
    ["s:http|h:com|h:gueulemer|", "s:http|h:com|h:javert|"],
    ["s:http|h:com|h:gueulemer|", "s:http|h:com|h:eponine|"],
    ["s:http|h:com|h:gueulemer|", "s:http|h:com|h:gavroche|"],
    ["s:http|h:com|h:babet|", "s:http|h:com|h:valjean|"],
    ["s:http|h:com|h:babet|", "s:http|h:com|h:mmethenardier|"],
    ["s:http|h:com|h:babet|", "s:http|h:com|h:thenardier|"],
    ["s:http|h:com|h:babet|", "s:http|h:com|h:javert|"],
    ["s:http|h:com|h:babet|", "s:http|h:com|h:eponine|"],
    ["s:http|h:com|h:babet|", "s:http|h:com|h:gavroche|"],
    ["s:http|h:com|h:babet|", "s:http|h:com|h:gueulemer|"],
    ["s:http|h:com|h:claquesous|", "s:http|h:com|h:valjean|"],
    ["s:http|h:com|h:claquesous|", "s:http|h:com|h:mmethenardier|"],
    ["s:http|h:com|h:claquesous|", "s:http|h:com|h:thenardier|"],
    ["s:http|h:com|h:claquesous|", "s:http|h:com|h:javert|"],
    ["s:http|h:com|h:claquesous|", "s:http|h:com|h:eponine|"],
    ["s:http|h:com|h:claquesous|", "s:http|h:com|h:enjolras|"],
    ["s:http|h:com|h:claquesous|", "s:http|h:com|h:gueulemer|"],
    ["s:http|h:com|h:claquesous|", "s:http|h:com|h:babet|"],
    ["s:http|h:com|h:montparnasse|", "s:http|h:com|h:valjean|"],
    ["s:http|h:com|h:montparnasse|", "s:http|h:com|h:thenardier|"],
    ["s:http|h:com|h:montparnasse|", "s:http|h:com|h:javert|"],
    ["s:http|h:com|h:montparnasse|", "s:http|h:com|h:eponine|"],
    ["s:http|h:com|h:montparnasse|", "s:http|h:com|h:gavroche|"],
    ["s:http|h:com|h:montparnasse|", "s:http|h:com|h:gueulemer|"],
    ["s:http|h:com|h:montparnasse|", "s:http|h:com|h:babet|"],
    ["s:http|h:com|h:montparnasse|", "s:http|h:com|h:claquesous|"],
    ["s:http|h:com|h:toussaint|", "s:http|h:com|h:valjean|"],
    ["s:http|h:com|h:toussaint|", "s:http|h:com|h:cosette|"],
    ["s:http|h:com|h:toussaint|", "s:http|h:com|h:javert|"],
    ["s:http|h:com|h:child1|", "s:http|h:com|h:gavroche|"],
    ["s:http|h:com|h:child2|", "s:http|h:com|h:gavroche|"],
    ["s:http|h:com|h:child2|", "s:http|h:com|h:child1|"],
    ["s:http|h:com|h:brujon|", "s:http|h:com|h:thenardier|"],
    ["s:http|h:com|h:brujon|", "s:http|h:com|h:eponine|"],
    ["s:http|h:com|h:brujon|", "s:http|h:com|h:gavroche|"],
    ["s:http|h:com|h:brujon|", "s:http|h:com|h:gueulemer|"],
    ["s:http|h:com|h:brujon|", "s:http|h:com|h:babet|"],
    ["s:http|h:com|h:brujon|", "s:http|h:com|h:claquesous|"],
    ["s:http|h:com|h:brujon|", "s:http|h:com|h:montparnasse|"],
    ["s:http|h:com|h:mmehucheloup|", "s:http|h:com|h:gavroche|"],
    ["s:http|h:com|h:mmehucheloup|", "s:http|h:com|h:enjolras|"],
    ["s:http|h:com|h:mmehucheloup|", "s:http|h:com|h:courfeyrac|"],
    ["s:http|h:com|h:mmehucheloup|", "s:http|h:com|h:bahorel|"],
    ["s:http|h:com|h:mmehucheloup|", "s:http|h:com|h:bossuet|"],
    ["s:http|h:com|h:mmehucheloup|", "s:http|h:com|h:joly|"],
    ["s:http|h:com|h:mmehucheloup|", "s:http|h:com|h:grantaire|"],
]

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

print("\n:: Store network...")

use_index_batch_crawl = True

if use_index_batch_crawl:
    data = {}
    for source_lru, target_lru in LINKS:
        if source_lru in data:
            links = data[source_lru]
        else:
            links = []
        links.append(target_lru)
        data[source_lru] = links
    report = traph.index_batch_crawl(data)
    webentity_store.data["webentities"].update(report.created_webentities)
else:
    for lru in PAGES:
        # add page
        report = traph.add_page(lru)
        webentity_store.data["webentities"].update(report.created_webentities)

    # add links
    links_report = traph.add_links(LINKS)
    webentity_store.data["webentities"].update(links_report.created_webentities)

print("...data stored.")

# Log result
print("\nPages:")
for node, lru in traph.pages_iter():
    print(" - " + lru)

print("\nPage Links:")
i = 0
for source_lru, target_lru in traph.links_iter():
    i += 1
    print(" - %s\t->  %s" % (source_lru, target_lru))
print("Total: %s" % i)

print("\nWebentities:")
for weid, prefixes in list(webentity_store.data["webentities"].items()):
    print(
        " - Webentity %s\t%s + %s other prefixes"
        % (weid, prefixes[0], len(prefixes) - 1)
    )

print("\nFocus on Valjean:")
valjean_inlinks = traph.get_page_links(
    "s:http|h:com|h:valjean|",
    include_inbound=True,
    include_internal=False,
    include_outbound=False,
)
for source_lru, lru, weight in valjean_inlinks:
    print("\t<- (weight %s) \t%s" % (weight, source_lru))
print("")
valjean_outlinks = traph.get_page_links(
    "s:http|h:com|h:valjean|",
    include_inbound=False,
    include_internal=False,
    include_outbound=True,
)
for lru, target_lru, weight in valjean_outlinks:
    print("\t-> (weight %s) \t%s" % (weight, target_lru))

# import networkx as nx

# g = nx.Graph()

# w = traph.get_webentities_links()

# for source, targets in w.items():
#     source_label = webentity_store.data['webentities'][source][1]
#     g.add_node(source, label=source_label)

#     for target in targets:
#         target_label = webentity_store.data['webentities'][target][1]
#         g.add_node(target, label=target_label)
#         g.add_edge(source, target)

# nx.write_gexf(g, './scripts/data/dump.gexf')

traph.close()
