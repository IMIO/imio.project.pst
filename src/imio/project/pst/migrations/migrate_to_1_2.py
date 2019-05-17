# -*- coding: utf-8 -*-
from collective.documentgenerator.utils import update_oo_config
from collective.eeafaceted.collectionwidget.utils import _updateDefaultCollectionFor
from eea.facetednavigation.interfaces import ICriteria
from imio.helpers.content import richtextval
from imio.helpers.content import transitions
from imio.migrator.migrator import Migrator
from imio.project.pst import add_path
from imio.project.pst.setuphandlers import _ as _translate
from Products.CPUtils.Extensions.utils import mark_last_version

import logging


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

    def adapt_dashboards(self):
        # reindex representative_responsible
        self.pc.manage_reindexIndex(ids=['representative_responsible'])
        # update actions search
        for brain in self.pc(object_provides='imio.project.pst.interfaces.IImioPSTProject'):
            pst = brain.getObject()
            folder = pst['pstactions']
            if u'representativeresponsible' in [cid for cid, crit in ICriteria(folder).items()]:
                continue
            xmlpath = add_path('faceted_conf/pstaction.xml')
            folder.unrestrictedTraverse('@@faceted_exportimport').import_xml(import_file=open(xmlpath))
            _updateDefaultCollectionFor(folder, folder['all'].UID())

    def run(self):

        # check if oo port must be changed
        update_oo_config()

        self.runProfileSteps('imio.project.pst', steps=['typeinfo'])

        self.various_update()
        self.adapt_dashboards()

        self.upgradeAll()

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
