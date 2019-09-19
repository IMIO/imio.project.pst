# -*- coding: utf-8 -*-

from collective.documentgenerator.utils import update_oo_config
from imio.migrator.migrator import Migrator
from Products.CPUtils.Extensions.utils import mark_last_version

import logging


logger = logging.getLogger('imio.project.pst')


class Migrate_To_1_3(Migrator):

    def __init__(self, context):
        Migrator.__init__(self, context)
        self.pc = self.portal.portal_catalog
        self.ps = self.portal.portal_setup

    def run(self):

        # check if oo port must be changed
        update_oo_config()

        self.runProfileSteps('imio.project.pst', steps=['catalog', 'typeinfo', 'viewlets', 'workflow'])
        self.runProfileSteps('imio.project.pst', steps=['repositorytool'], profile='demo')

        self.adapt_collections()

        # templates
        self.runProfileSteps('imio.project.pst', steps=['imioprojectpst-update-templates'], profile='update')
        self.runProfileSteps('imio.project.pst', steps=['imioprojectpst-templates'], profile='default')

        self.upgradeAll(omit=['imio.project.pst:default'])

        for prod in ['plonetheme.imioapps']:
            mark_last_version(self.portal, product=prod)

        # Reorder css and js
        self.runProfileSteps('imio.project.pst', steps=['cssregistry', 'jsregistry'])

        # Display duration
        self.finish()

    def adapt_collections(self):
        """ Include subactions in existing action dashboard collections """
        pstactions = self.pc.searchResults(
            portal_type="Folder",
            object_provides="imio.project.pst.interfaces.IActionDashboardBatchActions"
        )
        for pstaction in pstactions:
            for brain in self.pc.searchResults(
                    {'path': {'query': pstaction.getPath()},
                     'portal_type': 'DashboardCollection'}
            ):
                col = brain.getObject()
                for parameter in col.query:
                    if parameter['i'] == 'portal_type':
                        parameter['v'] = [u'pstaction', u'pstsubaction']
                col.query = list(col.query)  # need this to persist change
        # deactivate states collections to lighten menu
        for brain in self.pc(portal_type='DashboardCollection'):
            if brain.id.startswith('searchfor_'):
                obj = brain.getObject()
                obj.enabled = False
                obj.reindexObject(idxs=['enabled'])


def migrate(context):
    Migrate_To_1_3(context).run()
