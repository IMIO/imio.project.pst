# -*- coding: utf-8 -*-
from collective.documentgenerator.utils import update_oo_config
from collective.eeafaceted.collectionwidget.interfaces import ICollectionCategories
from collective.eeafaceted.collectionwidget.utils import _updateDefaultCollectionFor
from collective.task.interfaces import ITaskContentMethods
from eea.facetednavigation.criteria.handler import Criteria
from eea.facetednavigation.criteria.interfaces import ICriteria
from eea.facetednavigation.interfaces import IFacetedNavigable
from eea.facetednavigation.layout.interfaces import IFacetedLayout
from eea.facetednavigation.settings.interfaces import IDisableSmartFacets
from eea.facetednavigation.settings.interfaces import IHidePloneLeftColumn
from eea.facetednavigation.settings.interfaces import IHidePloneRightColumn
from imio.helpers.content import richtextval
from imio.helpers.content import transitions
from imio.migrator.migrator import Migrator
from imio.project.pst import add_path
from imio.project.pst.content.action import IPSTAction
from imio.project.pst.content.operational import IOperationalObjective
from imio.project.pst.content.strategic import IStrategicObjective
from imio.project.pst.interfaces import IActionDashboardBatchActions
from imio.project.pst.interfaces import IImioPSTProject
from imio.project.pst.interfaces import IOODashboardBatchActions
from imio.project.pst.interfaces import IOSDashboardBatchActions
from imio.project.pst.interfaces import ITaskDashboardBatchActions
from imio.project.pst.setuphandlers import _ as _translate
from imio.project.pst.setuphandlers import configure_task_config
from imio.project.pst.setuphandlers import configure_task_rolefields
from plone.app.contenttypes.interfaces import IPloneAppContenttypesLayer
# Deprecated
#from plone.app.contenttypes.migration.migration import BaseCustomMigator
#from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes
from Products.CMFPlone.utils import base_hasattr
from Products.CPUtils.Extensions.utils import mark_last_version
from zope.component import getAdapter
from zope.component import getMultiAdapter
from zope.interface import alsoProvides

import logging


logger = logging.getLogger('imio.project.pst')

interfaces = [
    ICollectionCategories,
    IDisableSmartFacets,
    IFacetedNavigable,
    IHidePloneLeftColumn,
    IHidePloneRightColumn,
]


# Deprecated
# class FolderMigrator(BaseCustomMigator):
#     """ Folder migration"""
#
#     def migrate(self, old, new):
#         new_path = "/".join(new.getPhysicalPath())
#         for iface in interfaces:
#             if iface.providedBy(old):
#                 alsoProvides(new, iface)
#                 logger.warn("{0} also provides {1}".format(new_path, str(iface)))
#
#         if old.getConstrainTypesMode() != 0:
#             behaviour = ISelectableConstrainTypes(new)
#             behaviour.setConstrainTypesMode(1)
#             if old.getConstrainTypesMode() == 1:
#                 behaviour.setLocallyAllowedTypes(old.getLocallyAllowedTypes())
#                 behaviour.setImmediatelyAddableTypes(old.getImmediatelyAddableTypes())
#
#         if IFacetedNavigable.providedBy(old):
#             criteria = Criteria(new)
#             criteria._update(ICriteria(old).criteria)
#             IFacetedLayout(new).update_layout('faceted-table-items')
#             logger.warn("Added faceted criteria and layout to {0}".format(new_path))


class Migrate_To_1_1(Migrator):

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
        self.portal.contacts.exclude_from_nav = True
        self.portal.contacts.reindexObject(['exclude_from_nav'])
        #Hiding folder contents
        self.portal.manage_permission('List folder contents', ('Manager', 'Site Administrator'), acquire=0)
        paob = self.portal.portal_actions.object_buttons
        for act in ('faceted.sync', 'faceted.disable', 'faceted.enable', 'faceted.search.disable',
                    'faceted.search.enable', 'faceted.actions.disable', 'faceted.actions.enable',
                    'ical_import_enable', 'ical_import_disable'):
            if act in paob:
                paob[act].visible = False

    def AT2Dx(self):
        if self.portal['front-page'].meta_type == 'Dexterity Item':
            return
        request = getattr(self.portal, 'REQUEST', None)
        self.reinstall(['plone.app.contenttypes:default'])
        alsoProvides(request, IPloneAppContenttypesLayer)
        migration_view = getMultiAdapter((self.portal, request), name=u'migrate_from_atct')
        results = migration_view(migrate=1, content_types=['Document', 'Folder', 'BlobFile'])
        logger.warn(results)

    def migrate_tasks(self):
        configure_task_config(self.portal)
        configure_task_rolefields(self.portal, force=True)
        brains = self.pc(portal_type='task', sort_on='path')
        logger.info("Setting parent fields on {:d} tasks".format(len(brains)))
        for brain in brains:
            adapted = getAdapter(brain.getObject(), ITaskContentMethods)
            fields = adapted.get_parents_fields()
            # logger.info("Setting parent fields '{}' on '{}'".format(fields.keys(),
            # adapted.context.absolute_url_path()))
            for field in fields:
                adapted.set_parents_value(field,
                                          adapted.calculate_parents_value(field, fields[field]))

    def adapt_dashboards(self):
        # mark dashboards
        for brain in self.pc(object_provides='imio.project.pst.interfaces.IImioPSTProject'):
            pst = brain.getObject()
            for id, inf in (('strategicobjectives', IOSDashboardBatchActions),
                            ('operationalobjectives', IOODashboardBatchActions),
                            ('pstactions', IActionDashboardBatchActions),
                            ('tasks', ITaskDashboardBatchActions)):
                folder = pst[id]
                logger.info("Adding interface '{}' on '{}'".format(inf.__identifier__, folder.absolute_url_path()))
                alsoProvides(folder, inf)
                if id == 'operationalobjectives':
                    xmlpath = add_path('faceted_conf/operationalobjective.xml')
                    folder.unrestrictedTraverse('@@faceted_exportimport').import_xml(import_file=open(xmlpath))
                    _updateDefaultCollectionFor(folder, folder['all'].UID())
        for inf, marker in ((IImioPSTProject, IOSDashboardBatchActions),
                            (IStrategicObjective, IOODashboardBatchActions),
                            (IOperationalObjective, IActionDashboardBatchActions),
                            (IPSTAction, ITaskDashboardBatchActions)):
            logger.info("Setting interface '{}' on '{}' objects".format(marker.__identifier__, inf.__identifier__))
            for brain in self.pc(object_provides=inf.__identifier__):
                alsoProvides(brain.getObject(), marker)

    def run(self):
        self.upgradeProfile('collective.messagesviewlet:default')
        # call the following to correct criterion to avoid error messages in dashboard upgrade, where there was a typo
        self.upgradeProfile('collective.eeafaceted.collectionwidget:default')
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
        self.upgradeProfile('collective.contact.plonegroup:default')
        self.upgradeProfile('collective.documentgenerator:default')
        self.runProfileSteps('imio.helpers', steps=['jsregistry'])
        self.upgradeProfile('collective.task:default')

        # ordering viewlets
        self.runProfileSteps('imio.project.core', steps=['viewlets'], profile='default')

        self.runProfileSteps('imio.project.pst', steps=['actions', 'typeinfo'])
# 'catalog', 'componentregistry', 'jsregistry', 'portlets', 'propertiestool', 'plone.app.registry', 'workflow'

        self.AT2Dx()

        self.adapt_dashboards()

        self.migrate_tasks()

        # update security settings
        # self.portal.portal_workflow.updateRoleMappings()

        self.various_update()

        # templates
        self.runProfileSteps('imio.project.pst', steps=['imioprojectpst-update-templates'], profile='update')
        self.runProfileSteps('imio.project.pst', steps=['imioprojectpst-templates'], profile='default')

        # self.upgradeAll()

        # update portal_catalog
        # self.refreshDatabase()

        # check if oo port must be changed
        update_oo_config()

        for prod in ['collective.eeafaceted.colletionwidget', 'collective.eeafaceted.z3ctable',
                     'collective.behavior.talcondition', 'collective.compoundcriterion', 'collective.ckeditor',
                     'collective.contact.widget', 'collective.plonefinder', 'collective.quickupload',
                     'collective.z3cform.datagridfield', 'collective.z3cform.datetimewidget', 'communesplone.layout',
                     'dexterity.localroles', 'dexterity.localrolesfield', 'eea.facetednavigation', 'eea.jquery',
                     'imio.dashboard', 'imio.history', 'imio.project.core', 'imio.project.pst', 'PasswordStrength',
                     'plone.app.collection', 'plone.app.dexterity', 'plone.app.versioningbehavior',
                     'plone.formwidget.autocomplete', 'plone.formwidget.contenttree',
                     'plone.formwidget.datetime', 'plonetheme.classic', 'plonetheme.imioapps']:
            mark_last_version(self.portal, product=prod)

        # Reorder css and js
        self.runProfileSteps('imio.project.pst', steps=['cssregistry', 'jsregistry'])

        # Display duration
        self.finish()


def migrate(context):
    Migrate_To_1_1(context).run()
