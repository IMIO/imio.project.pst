# -*- coding: utf-8 -*-
import logging
from zope.component import getUtility
from zope.i18n import translate
from zope.globalrequest import getRequest
from plone import api
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.utils import base_hasattr, safe_unicode

from Products.CPUtils.Extensions.utils import mark_last_version
from collective.contact.plonegroup.config import FUNCTIONS_REGISTRY

from imio.helpers.catalog import addOrUpdateIndexes
from imio.migrator.migrator import Migrator
from imio.project.pst.setuphandlers import (
    adaptDefaultPortal, configureDashboard, configure_actions_panel, configure_rolefields, reimport_faceted_config,
    add_plonegroups_to_registry, _addTemplatesDirectory)
from imio.project.pst import _


logger = logging.getLogger('imio.project.pst')


class Migrate_To_1_0(Migrator):

    def __init__(self, context):
        Migrator.__init__(self, context)
        self.pc = self.portal.portal_catalog

    def migrate_pst_action_fields(self):
        for brain in self.pc(portal_type="pstaction"):
            action = brain.getObject()
            action.manager = [m[:-13] for m in action.manager if m.endswith('_actioneditor')]
            if base_hasattr(action, 'work_plan') and action.work_plan:
                title = translate(
                    _("Work plan: ${action_title}",
                      mapping={'action_title': safe_unicode(action.Title())}),
                    context=getRequest())
                task = api.content.create(
                    container=action,
                    title=title,
                    type='task',
                )
                task.task_description = action.work_plan.raw
                # action.work_plan = None

    def migrate_templates(self):
        folder = self.portal['templates']
        folder.setLocallyAllowedTypes(['ConfigurablePODTemplate', 'StyleTemplate', 'DashboardPODTemplate'])
        folder.setImmediatelyAddableTypes(['ConfigurablePODTemplate', 'StyleTemplate', 'DashboardPODTemplate'])
        _addTemplatesDirectory(self.context._getImportContext('imio.project.pst:default'))

    def various_update(self):
        # Add new function
        registry = getUtility(IRegistry)
        if not [r for r in registry[FUNCTIONS_REGISTRY] if r['fct_id'] == 'admin_resp']:
            registry[FUNCTIONS_REGISTRY] = registry[FUNCTIONS_REGISTRY] + [{'fct_title': u"Responsable administratif",
                                                                            'fct_id': u'admin_resp'}]

        # Adapt default portal:
        adaptDefaultPortal(self.portal)

        # replace front-page
        # TO BE DONE

    def run(self):
        # Removed old import step
        setup = api.portal.get_tool('portal_setup')
        ir = setup.getImportStepRegistry()
        # /cputils_removeStep?step=imioprojectpst-adaptDefaultPortal
        if 'imioprojectpst-adaptDefaultPortal' in ir._registered:
            del ir._registered['imioprojectpst-adaptDefaultPortal']
        self.reinstall([
            'dexterity.localrolesfield:default',
        ])
        self.runProfileSteps(
            'imio.project.pst',
            steps=[
                'actions', 'catalog', 'componentregistry', 'portlets', 'propertiestool',
                'plone.app.registry', 'typeinfo', 'workflow'
            ]
        )
        self.reinstall([
            'collective.documentgenerator:default',
            'collective.externaleditor:default',
            'collective.messagesviewlet:messages',
            'collective.task:default',
            'imio.dashboard:default',
            'plonetheme.imioapps:pstskin',
        ])

        self.various_update()

        indexes_to_add = {
            'categories': ('KeywordIndex', {}),
            'priority': ('FieldIndex', {}),
            'representative_responsible': ('KeywordIndex', {}),
            'administrative_responsible': ('KeywordIndex', {}),
            'manager': ('KeywordIndex', {}),
            'planned_begin_date': ('DateIndex', {}),
            'planned_end_date': ('DateIndex', {}),
            'effective_begin_date': ('DateIndex', {}),
            'effective_end_date': ('DateIndex', {}),
            'health_indicator': ('FieldIndex', {}),
            'progress': ('FieldIndex', {}),
            'extra_concerned_people': ('ZCTextIndex', {}),
        }
        addOrUpdateIndexes(
            self.context, indexes_to_add)

        # remove the old collections and configure the dashboard
        if 'collections' in self.portal.pst:
            api.content.delete(obj=self.portal.pst['collections'])
        for brain in self.pc(portal_type='Collection', path='/'.join(self.portal.pst.getPhysicalPath())):
            api.content.delete(obj=brain.getObject())

        configureDashboard(self.portal.pst)
        self.portal.pst.setLayout('view')

        self.runProfileSteps('imio.project.pst', steps=['portlets'], profile='demo')

        # migrate oo fields
        brains = self.pc(portal_type="operationalobjective")
        for brain in brains:
            oo = brain.getObject()
            oo.administrative_responsible = [r[:-13] for r in oo.administrative_responsible
                                             if r.endswith('_actioneditor')]
            oo.manager = [m[:-13] for m in oo.manager if m.endswith('_actioneditor')]

        self.migrate_pst_action_fields()

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

        add_plonegroups_to_registry()
        configure_actions_panel(self.portal)
        configure_rolefields(self.portal)

        # migrate to documentgenerator
        self.migrate_templates()

        self.upgradeAll()

        # update portal_catalog
        self.refreshDatabase()

        for prod in []:
            mark_last_version(self.portal, product=prod)

        # Reorder css and js
        self.runProfileSteps('imio.project.pst', steps=['cssregistry', 'jsregistry'])

        # Display duration
        self.finish()


def migrate(context):
    Migrate_To_1_0(context).run()
