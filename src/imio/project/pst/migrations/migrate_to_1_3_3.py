# -*- coding: utf-8 -*-

import logging

from collective.contact.plonegroup.config import FUNCTIONS_REGISTRY
from imio.migrator.migrator import Migrator
from imio.project.core.utils import getProjectSpace
from imio.project.pst.setuphandlers import _ as _translate, COLUMNS_FOR_CONTENT_TYPES, createDashboardCollections
from plone import api
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

logger = logging.getLogger('imio.project.pst')


def migrate_plonegroups():
    """Added a new representative responsible function."""
    registry = getUtility(IRegistry)
    to_add = []
    if not [r for r in registry[FUNCTIONS_REGISTRY] if r['fct_id'] == 'repr_resp']:
        to_add.append(
            {'fct_title': u"Responsable mandataire", 'fct_id': u'repr_resp', 'fct_orgs': [],
             'fct_management': False, 'enabled': True}
        )
    if to_add:
        registry[FUNCTIONS_REGISTRY] = registry[FUNCTIONS_REGISTRY] + to_add


def add_representative_responsible_collection():
    """Added an additional collection "Which I am representative responsible" for operational objective and pstaction"""
    pst = api.portal.get().pst
    for tup in [('operationalobjectives', ['operationalobjective']), ('pstactions', ['pstaction'])]:
        col_folder = tup[0]
        content_type = tup[1]
        folder = pst[col_folder]
        ps_path = '/'.join(getProjectSpace(folder).getPhysicalPath())
        collections = [
            {
                'id': 'i-am-representative_responsible',
                'tit': _translate("Which I am representative responsible"),
                'subj': ('search',),
                'query': [
                    {'i': 'portal_type', 'o': 'plone.app.querystring.operation.selection.is', 'v': content_type},
                    {'i': 'CompoundCriterion', 'o': 'plone.app.querystring.operation.compound.is',
                     'v': 'user-is-representative-responsible'},
                    {'i': 'path', 'o': 'plone.app.querystring.operation.string.path', 'v': ps_path}
                ],
                'cond': u"",
                'bypass': [],
                'flds': COLUMNS_FOR_CONTENT_TYPES[content_type[0]],
                'sort': u'sortable_title',
                'rev': False,
                'count': False
            },
        ]
        createDashboardCollections(folder, collections, 1)


class MigrateTo133(Migrator):

    def __init__(self, context):
        Migrator.__init__(self, context)

    def run(self):
        # Added a new representative responsible function
        migrate_plonegroups()

        # Added an additional collection "Which I am representative responsible" for operational objective and pstaction
        add_representative_responsible_collection()

        # Display duration
        self.finish()


def migrate(context):
    MigrateTo133(context).run()
