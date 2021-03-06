# -*- coding: utf-8 -*-
from collective.contact.plonegroup.utils import get_own_organization
from collective.documentgenerator.utils import update_oo_config
from imio.helpers.content import richtextval
from imio.helpers.content import transitions
from imio.migrator.migrator import Migrator
from imio.project.pst.setuphandlers import _ as _translate
from imio.project.pst.setuphandlers import reimport_faceted_config
from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes
from Products.CPUtils.Extensions.utils import mark_last_version

import logging
import os


logger = logging.getLogger('imio.project.pst')


class Migrate_To_1_2(Migrator):

    def __init__(self, context):
        Migrator.__init__(self, context)
        self.pc = self.portal.portal_catalog
        self.ps = self.portal.portal_setup

    def various_update(self):
        # replace front-page
        frontpage = getattr(self.portal, 'front-page')
        frontpage.title = _translate("front_page_title")
        frontpage.description = _translate("front_page_descr")
        frontpage.text = richtextval(_translate("front_page_text"))
        transitions(frontpage, ('retract', 'publish_internally'))
        frontpage.reindexObject()
        self.portal.templates.layout = 'dg-templates-listing'
        # plonegroup-organization
        pgo = get_own_organization()
        behaviour = ISelectableConstrainTypes(pgo)
        behaviour.setConstrainTypesMode(1)
        behaviour.setLocallyAllowedTypes([])
        behaviour.setImmediatelyAddableTypes([])
        ISelectableConstrainTypes(pgo['echevins']).setConstrainTypesMode(0)
        ISelectableConstrainTypes(pgo['services']).setConstrainTypesMode(0)

    def adapt_dashboards(self):
        # reindex representative_responsible
        self.pc.manage_reindexIndex(ids=['representative_responsible'])
        # update actions search
        for brain in self.pc(object_provides='imio.project.pst.interfaces.IImioPSTProject'):
            pst = brain.getObject()
            mapping = {
                'strategicobjectives': 'strategicobjective',
                'operationalobjectives': 'operationalobjective',
                'pstactions': 'pstaction',
                'tasks': 'task'
            }
            for col_folder_id, content_type in mapping.iteritems():
                col_folder = pst[col_folder_id]
                reimport_faceted_config(col_folder, xml='{}.xml'.format(content_type),
                                        default_UID=col_folder['all'].UID())
        # collections
        brains = self.catalog.searchResults(portal_type='DashboardCollection')
        for brain in brains:
            col = brain.getObject()
            col.sort_on = None
            col.sort_reversed = None
            if (os.path.basename(os.path.dirname(brain.getPath())) in ('operationalobjectives', 'pstactions')
                    and 'parents' not in col.customViewFields):
                nl = list(col.customViewFields)
                nl.insert(col.customViewFields.index(u'pretty_link') + 1, u'parents')
                col.customViewFields = tuple(nl)
            if (os.path.basename(os.path.dirname(brain.getPath())) == 'tasks'
                    and 'parents' not in col.customViewFields):
                nl = list(col.customViewFields)
                nl[nl.index(u'task_parent')] = u'parents'
                col.customViewFields = tuple(nl)

    def update_items(self):
        for brain in self.pc(portal_type=('strategicobjective', 'operationalobjective')):
            obj = brain.getObject()
            if obj.categories is None or isinstance(obj.categories, (list, tuple)):
                continue
            obj.categories = [obj.categories]
            obj.reindexObject()

    def run(self):

        # check if oo port must be changed
        update_oo_config()

        self.runProfileSteps('imio.project.pst', steps=['actions', 'jsregistry', 'plone.app.registry', 'typeinfo'])

        self.various_update()
        self.adapt_dashboards()
        self.update_items()

        # templates
        self.runProfileSteps('imio.project.pst', steps=['imioprojectpst-update-templates'], profile='update')
        self.runProfileSteps('imio.project.pst', steps=['imioprojectpst-templates'], profile='default')

        self.upgradeAll(omit=['imio.project.pst:default'])

        # update portal_catalog
        # self.refreshDatabase()

        for prod in ['plonetheme.imioapps']:
            mark_last_version(self.portal, product=prod)

        # Reorder css and js
        self.runProfileSteps('imio.project.pst', steps=['cssregistry', 'jsregistry'])

        # Display duration
        self.finish()


def migrate(context):
    Migrate_To_1_2(context).run()
