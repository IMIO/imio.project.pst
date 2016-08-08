# -*- coding: utf-8 -*-
import logging
from zope.component import getUtility
from plone import api
from plone.registry.interfaces import IRegistry

from collective.contact.plonegroup.config import FUNCTIONS_REGISTRY

from imio.helpers.catalog import addOrUpdateIndexes
from imio.migrator.migrator import Migrator
from imio.project.pst.setuphandlers import (
    configureDashboard, configure_rolefields, reimport_faceted_config)


logger = logging.getLogger('imio.project.pst')


class Migrate_To_0_4(Migrator):

    def __init__(self, context):
        Migrator.__init__(self, context)

    def various_update(self):
        # Removed old import step
        setup = api.portal.get_tool('portal_setup')
        ir = setup.getImportStepRegistry()
        if 'imioprojectpst-adaptDefaultPortal' in ir._registered:
            del ir._registered['imioprojectpst-adaptDefaultPortal']
        # Add new function
        registry = getUtility(IRegistry)
        if not [r for r in registry[FUNCTIONS_REGISTRY] if r['fct_id'] == 'administrative_responsible']:
            registry[FUNCTIONS_REGISTRY] = registry[FUNCTIONS_REGISTRY] + [{'fct_title': u"Responsable administratif",
                                                                            'fct_id': u'administrative_responsible'}]

    def run(self):
        self.various_update()
        self.runProfileSteps('imio.project.pst', steps=['catalog', 'portlets', 'propertiestool'])
        self.reinstall([
            'imio.project.core:default',
            'imio.dashboard:default',
            'plonetheme.imioapps:pstskin',
        ])

        indexes_to_add = {
            'categories': ('KeywordIndex', {}),
            'priority': ('FieldIndex', {}),
        }
        addOrUpdateIndexes(
            self.context, indexes_to_add)

        # remove the old collections and configure the dashboard
        if 'collections' in self.portal.pst:
            api.content.delete(obj=self.portal.pst['collections'])

        configureDashboard(self.portal.pst)
        # update faceted navigation configs
        mapping = {
            'strategicobjectives': 'strategicobjective',
            'operationalobjectives': 'operationalobjective',
            'pstactions': 'pstaction',
        }
        for col_folder_id, content_type in mapping.iteritems():
            col_folder = self.portal.pst[col_folder_id]
            reimport_faceted_config(
                col_folder,
                xml='{}.xml'.format(content_type),
                default_UID=col_folder['all'].UID())

        configure_rolefields()

        # update portal_catalog
        self.refreshDatabase()

        # Display duration
        self.finish()


def migrate(context):
    Migrate_To_0_4(context).run()
