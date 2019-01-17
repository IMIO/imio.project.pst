# -*- coding: utf-8 -*-
from collective.eeafaceted.collectionwidget.utils import _updateDefaultCollectionFor
from imio.helpers.content import transitions
from imio.migrator.migrator import Migrator
from imio.project.pst import add_path
from imio.project.pst.setuphandlers import _ as _translate
from Products.CMFPlone.utils import base_hasattr
from Products.CPUtils.Extensions.utils import mark_last_version

import logging


logger = logging.getLogger('imio.project.pst')


class Migrate_To_1_1(Migrator):

    def __init__(self, context):
        Migrator.__init__(self, context)
        self.pc = self.portal.portal_catalog
        self.ps = self.portal.portal_setup

    def various_update(self):
        # replace front-page
        frontpage = getattr(self.portal, 'front-page')
        frontpage.setTitle(_translate("front_page_title"))
        frontpage.setDescription(_translate("front_page_descr"))
        frontpage.setText(_translate("front_page_text"), mimetype='text/html')
        transitions(frontpage, ('retract', 'publish_internally'))
        frontpage.reindexObject()

    def run(self):
        # upgrade imio.dashboard
        self.upgradeProfile('imio.dashboard:default')
        # skip 4320 to 4330. Do it programmatically
        ckp = self.portal.portal_properties.ckeditor_properties
        if not ckp.hasProperty('skin'):
            if base_hasattr(ckp, 'skin'):
                delattr(ckp, 'skin')
            ckp.manage_addProperty('skin', 'moono-lisa', 'string')
        self.ps.setLastVersionForProfile('collective.ckeditor:default', '4330')
        self.upgradeProfile('collective.ckeditor:default')
        self.upgradeProfile('plonetheme.imioapps:default')
        self.upgradeProfile('imio.actionspanel:default')
        # add icon to existing actions
        self.runProfileSteps('plonetheme.imioapps', steps=['actions'], profile='default')
        self.upgradeProfile('collective.contact.core:default')


        for brain in self.pc(portal_type='projectspace'):
            ps = brain.getObject()
            if 'operationalobjectives' not in ps:
                continue
            folder = ps['operationalobjectives']
            xmlpath = add_path('faceted_conf/operationalobjective.xml')
            folder.unrestrictedTraverse('@@faceted_exportimport').import_xml(import_file=open(xmlpath))
            _updateDefaultCollectionFor(folder, folder['all'].UID())

        # ordering viewlets
        self.runProfileSteps('imio.project.core', steps=['viewlets'], profile='default')

#        self.runProfileSteps('imio.project.pst', steps=['actions', 'catalog', 'componentregistry', 'jsregistry',
#                                                        'portlets', 'propertiestool', 'plone.app.registry',
#                                                        'typeinfo', 'workflow'])

        # update security settings
        # self.portal.portal_workflow.updateRoleMappings()

        self.various_update()

        # self.upgradeAll()

        # update portal_catalog
        # self.refreshDatabase()

        for prod in ['collective.eeafaceted.colletionwidget', 'collective.eeafaceted.z3ctable',
                     'collective.behavior.talcondition', 'collective.compoundcriterion', 'collective.ckeditor',
                     'collective.plonefinder', 'collective.quickupload', 'collective.z3cform.datetimewidget',
                     'eea.facetednavigation', 'eea.jquery', 'imio.dashboard', 'imio.project.core',
                     'imio.project.pst', 'plone.app.collection', 'plone.app.dexterity',
                     'plone.formwidget.autocomplete', 'plone.formwidget.contenttree', 'plone.formwidget.datetime',
                     'plonetheme.classic', 'plonetheme.imioapps']:
            mark_last_version(self.portal, product=prod)

        # Reorder css and js
        self.runProfileSteps('imio.project.pst', steps=['cssregistry', 'jsregistry'])

        # Display duration
        self.finish()


def migrate(context):
    Migrate_To_1_1(context).run()
