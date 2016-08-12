""" Custom catalog
"""
from copy import deepcopy
import logging
from zope.event import notify
from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from BTrees.IIBTree import IIBucket
from eea.facetednavigation.events import QueryWillBeExecutedEvent
from eea.facetednavigation.search.interfaces import IFacetedCatalog
from eea.facetednavigation.search.interfaces import ICollection
from eea.facetednavigation.search import parseFormquery

try:
    from plone.app.contenttypes import interfaces as PACI
    from plone.app.contenttypes.behaviors.collection import \
            ICollection as ICollection_behavior
    HAS_PAT = True
except ImportError:
    HAS_PAT = False

logger = logging.getLogger('eea.facetednavigation.search.catalog')

from BTrees.IIBTree import weightedIntersection, IISet
from eea.facetednavigation.search.catalog import FacetedCatalog as eeaFacetedCatalog


class FacetedCatalog(eeaFacetedCatalog):

    def __call__(self, context, **query):
        # return super(FacetedCatalog, self).__call__(context, **query)
        ctool = getToolByName(context, 'portal_faceted', None)
        if ctool:
            search = ctool.search
        else:
            logger.debug('portal_faceted not present, using portal_catalog')
            ctool = getToolByName(context, 'portal_catalog')
            search = ctool.searchResults

        # Also get query from Topic
        buildQuery = getattr(context, 'buildQuery', None)
        newquery = buildQuery and buildQuery() or {}
        formquery = None

        # Get query from Collection
        if HAS_PAT:
            if PACI.ICollection.providedBy(context):
                infos = ICollection_behavior(context)
                sort_order = ('descending'
                              if infos.sort_reversed
                              else 'ascending')
                sort_on = infos.sort_on
                formquery = infos.query

        if ICollection.providedBy(context):
            getRawQuery = getattr(context, 'getRawQuery', lambda: [])
            formquery = getRawQuery()

            getSortOn = getattr(context, 'getSort_on', lambda: None)
            sort_on = getSortOn()

            if sort_on:
                getSortReversed = getattr(
                    context, 'getSort_reversed', lambda: None)
                sort_order = getSortReversed()
                if sort_order:
                    sort_order = 'descending'
                else:
                    sort_order = 'ascending'
            else:
                sort_order = None

        if formquery is not None:
            newquery = parseFormquery(context, formquery, sort_on, sort_order)

        if not isinstance(newquery, dict):
            newquery = {}

        # Avoid mixing sorting params from faceted and collection
        if 'sort_on' not in query:
            query.pop('sort_order', None)

        if 'sort_on' in query and 'sort_order' not in query:
            newquery.pop('sort_order', None)

        newquery.update(query)

        notify(QueryWillBeExecutedEvent(context, newquery))

        # code above is unchanged from original code

        # example of query:
        #{'sort_order': 'descending',
        # 'Language': ['fr', ''],
        # 'portal_type': {'query': ['operationalobjective']},
        # 'sort_on': 'created',
        # ':has_child': {'query': {
        #     'portal_type': {'query': ['pstaction']},
        #     'planned_end_date': {'query': DateTime('2016/08/12 12:49:6.218718 GMT+2'), 'range': 'max'}}}}

        has_child_filters = [k for k in newquery.keys()
                             if k.startswith(':has_child')]
        if len(has_child_filters) > 1:
            raise Exception('We only support one :has_child filter')

        if has_child_filters:
            # TODO: Possible optimization is to create a fake index parentRID which return the ISet of given rids,
            # This is allow to do the sort after the intersection.
            # we can't use limit or b_size for the main query because we do an intersect after.
            # Facetednav doesn't seem to give them anyway.
            newquery.pop('limit', None)  # not needed if we use a fake parentRID index
            newquery.pop('b_size', None)  # not needed if we use a fake parentRID index
            has_child_filter = deepcopy(newquery[has_child_filters[0]]['query'])
            # be sure we don't do a useless sort and we have all results
            has_child_filter.pop('sort_on', None)
            has_child_filter.pop('sort_order', None)
            has_child_filter.pop('limit', None)
            has_child_filter.pop('b_size', None)
            children_results = search(**has_child_filter)
            parentRIDs = IISet()
            for b in children_results:
                # TODO: possible optimization is to add parentRID as brain metadata
                parentRID = ctool._catalog.uids.get(
                    '/'.join(b.getPath().split('/')[:-1]))
                parentRIDs.add(parentRID)

            # newquery['parentRID'] = parentRIDs  # if we use a fake index, and the intersection below can be removed
            brains = search(**newquery)
            # brains should be a LazyMap, access direct to brains._seq which is a list of rids
            # instead of doing IISet(brain.getRID() for brain in brains)
            # We lose the order if we use weightedIntersection
            if not 'sort_on' in newquery:
                rset = weightedIntersection(IISet(brains._seq), parentRIDs)[1]
            else:
                rset = [rid for rid in brains._seq if rid in parentRIDs]

            len_rset = len(rset)
            brains = brains.__class__(brains._func, rset, len_rset, len_rset)
        else:
            brains = search(**newquery)

        return brains
