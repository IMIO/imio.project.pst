# -*- coding: utf-8 -*-

from imio.migrator.migrator import Migrator
from plone import api

import logging

logger = logging.getLogger('imio.project.pst')


class Migrate_To_0_3_1(Migrator):
    def __init__(self, context):
        Migrator.__init__(self, context)

    def set_tabular_view_to_pst_collections(self):
        """
        """
        logger.info('set tabular view to pst collections ...')
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog(portal_type='Collection')
        for brain in brains:
            collection = brain.getObject()
            collection.setLayout('tabular_view')
        logger.info('Done.')


    def run(self):
        self.set_tabular_view_to_pst_collections()
        # reinstall
        self.reinstall(profiles=[u'profile-imio.project.pst:default', ])
        # Display duration
        self.finish()


def migrate(context):
    Migrate_To_0_3_1(context).run()
