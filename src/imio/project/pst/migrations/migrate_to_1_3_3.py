# -*- coding: utf-8 -*-

import logging

from collective.contact.plonegroup.config import FUNCTIONS_REGISTRY
from imio.migrator.migrator import Migrator
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


class MigrateTo133(Migrator):

    def __init__(self, context):
        Migrator.__init__(self, context)

    def run(self):
        # Added a new representative responsible function
        migrate_plonegroups()

        # Display duration
        self.finish()


def migrate(context):
    MigrateTo133(context).run()
