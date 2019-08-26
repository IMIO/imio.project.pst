# -*- coding: utf-8 -*-
from imio.migrator.migrator import Migrator

import logging


logger = logging.getLogger('imio.project.pst')


class Migrate_To_1_3(Migrator):

    def __init__(self, context):
        Migrator.__init__(self, context)
        self.pc = self.portal.portal_catalog
        self.ps = self.portal.portal_setup

    def run(self):

        self.adapt_collections()

        # Display duration
        self.finish()

    def adapt_collections(self):
        """Include subactions in existing action dashboard collections"""
        pstactions = self.pc.searchResults(
            portal_type="Folder",
            object_provides="imio.project.pst.interfaces.IActionDashboardBatchActions"
        )[0]
        for brain in self.pc.searchResults(
                {'path': {'query': pstactions.getPath()},
                 'portal_type': 'DashboardCollection'}
        ):
            col = brain.getObject()
            for parameter in col.query:
                if parameter['i'] == 'portal_type':
                    parameter['v'] = [u'pstaction', u'pstsubaction']


def migrate(context):
    Migrate_To_1_3(context).run()
