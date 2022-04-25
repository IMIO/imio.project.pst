# -*- coding: utf-8 -*-

import logging

from collective.contact.plonegroup.config import FUNCTIONS_REGISTRY, ORGANIZATIONS_REGISTRY
from dexterity.localroles.utils import add_fti_configuration
from imio.migrator.migrator import Migrator
from imio.project.core.utils import getProjectSpace
from imio.project.pst.setuphandlers import _ as _translate, COLUMNS_FOR_CONTENT_TYPES, createDashboardCollections

logger = logging.getLogger('imio.project.pst')


def configure_representative_responsible_local_roles():
    config = {
        ('operationalobjective',): {
            'representative_responsible': {
                'achieved': {'repr_resp': {'roles': ['Reader']}},
                'created': {'repr_resp': {'roles': ['Reader']}},
                'ongoing': {'repr_resp': {'roles': ['Reader']}},
            },
        },
        ('pstaction', 'pstsubaction'): {
            'representative_responsible': {
                'created': {'actioneditor': {'roles': ['Reader']}},
                'to_be_scheduled': {'actioneditor': {'roles': ['Reader']}},
                'ongoing': {'actioneditor': {'roles': ['Reader']}},
                'terminated': {'actioneditor': {'roles': ['Reader']}},
                'stopped': {'actioneditor': {'roles': ['Reader']}},
            },
        },
    }
    for portal_types, roles_config in config.iteritems():
        for portal_type in portal_types:
            for keyname in roles_config:
                add_fti_configuration(portal_type, roles_config[keyname], keyname=keyname, force=False)


class MigrateTo133(Migrator):

    def __init__(self, context):
        Migrator.__init__(self, context)

    def run(self):
        # Added a new representative responsible function
        self.migrate_plonegroups()

        # Activate all aldermen organizations
        self.activate_all_aldermen_organizations()

        # Added an additional collection "Which I am representative responsible" for operational objective and pstaction
        self.add_representative_responsible_collection()

        # Configure representative responsible role for operational objectives and pst actions
        configure_representative_responsible_local_roles()

        # Display duration
        self.finish()

    def migrate_plonegroups(self):
        """Added a new representative responsible function."""
        registry = self.registry
        to_add = []
        if not [r for r in registry[FUNCTIONS_REGISTRY] if r['fct_id'] == 'repr_resp']:
            to_add.append(
                {'fct_title': u"Responsable mandataire", 'fct_id': u'repr_resp', 'fct_orgs': [],
                 'fct_management': False, 'enabled': True}
            )
        if to_add:
            registry[FUNCTIONS_REGISTRY] = registry[FUNCTIONS_REGISTRY] + to_add

    def activate_all_aldermen_organizations(self):
        """Activate all aldermen organizations"""
        registry = self.registry
        echevs = self.portal['contacts']['plonegroup-organization']['echevins'].objectItems()
        echev_uids = [echevin[1].UID() for echevin in echevs]
        to_add = [echev_uid for echev_uid in echev_uids if echev_uid not in registry[ORGANIZATIONS_REGISTRY]]
        if to_add:
            registry[ORGANIZATIONS_REGISTRY] = registry[ORGANIZATIONS_REGISTRY] + to_add

    def add_representative_responsible_collection(self):
        """
        Added an additional collection "Which I am representative responsible" for operational objective and pstaction
        """
        pst = self.portal.pst
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


def migrate(context):
    MigrateTo133(context).run()
