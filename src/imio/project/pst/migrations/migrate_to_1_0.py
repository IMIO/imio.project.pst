# -*- coding: utf-8 -*-
import logging
from zope.i18n import translate
from zope.globalrequest import getRequest
from plone import api
from Products.CMFPlone.utils import base_hasattr, safe_unicode

from Products.CPUtils.Extensions.utils import mark_last_version

from imio.helpers.catalog import addOrUpdateIndexes
from imio.helpers.content import transitions
from imio.migrator.migrator import Migrator
from imio.project.pst.setuphandlers import (
    adaptDefaultPortal, add_plonegroups_to_registry, configureDashboard, configure_actions_panel, configure_rolefields,
    reimport_faceted_config, _addTemplatesDirectory)
from ..setuphandlers import _ as _translate
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
                title = translate(_("Work plan: ${action_title}",
                                    mapping={'action_title': safe_unicode(action.Title())}), context=getRequest())
                task = api.content.create(container=action, title=title, type='task')
                task.task_description = action.work_plan.raw
                # action.work_plan = None

    def migrate_templates(self):
        folder = self.portal['templates']
        folder.setLocallyAllowedTypes(['ConfigurablePODTemplate', 'StyleTemplate', 'DashboardPODTemplate'])
        folder.setImmediatelyAddableTypes(['ConfigurablePODTemplate', 'StyleTemplate', 'DashboardPODTemplate'])
        _addTemplatesDirectory(self.context._getImportContext('imio.project.pst:default'))

    def various_update(self):
        # Adapt default portal:
        adaptDefaultPortal(self.portal)
        # remove local roles on project spaces (old ones too)
        for brain in self.pc(portal_type='projectspace'):
            brain.getObject().manage_delLocalRoles(["pst_managers", "pst_editors", "pst_readers"])
        try:
            api.group.delete(groupname="pst_managers")
        except:
            pass

        # replace front-page
        frontpage = getattr(self.portal, 'front-page')
        frontpage.setTitle(_translate("front_page_title"))
        frontpage.setDescription(_translate("front_page_descr"))
        frontpage.setText(_translate("front_page_text"), mimetype='text/html')
        transitions(frontpage, ('retract', 'publish_internally'))
        frontpage.reindexObject()

    def run(self):
        # Removed old import step
        setup = api.portal.get_tool('portal_setup')
        ir = setup.getImportStepRegistry()
        # /cputils_removeStep?step=imioprojectpst-adaptDefaultPortal
        if 'imioprojectpst-adaptDefaultPortal' in ir._registered:
            del ir._registered['imioprojectpst-adaptDefaultPortal']
        self.upgradeProfile('collective.contact.core:default')
        self.upgradeProfile('collective.contact.plonegroup:default')
        self.upgradeProfile('plone.formwidget.masterselect:default')
        self.reinstall(['dexterity.localrolesfield:default'])
        self.runProfileSteps('imio.project.pst', steps=['actions', 'catalog', 'componentregistry', 'jsregistry',
                                                        'portlets', 'propertiestool', 'plone.app.registry',
                                                        'typeinfo', 'workflow'])
        # update security settings
        self.portal.portal_workflow.updateRoleMappings()

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
            reimport_faceted_config(col_folder, xml='{}.xml'.format(content_type), default_UID=col_folder['all'].UID())

        add_plonegroups_to_registry()
        configure_actions_panel(self.portal)
        configure_rolefields(self.portal)

        # migrate to documentgenerator
        self.migrate_templates()

        self.upgradeAll()

        # update portal_catalog
        self.refreshDatabase()

        for prod in ['collective.ckeditor', 'collective.contact.core', 'collective.contact.plonegroup',
                     'collective.plonefinder', 'collective.quickupload', 'collective.z3cform.datagridfield',
                     'imio.project.core', 'imio.project.pst', 'plonetheme.classic',
                     'plone.app.collection', 'plone.app.dexterity', 'plone.app.intid', 'plone.app.relationfield',
                     'plone.formwidget.masterselect', 'plone.formwidget.autocomplete', 'plone.formwidget.contenttree']:
            mark_last_version(self.portal, product=prod)

        # Reorder css and js
        self.runProfileSteps('imio.project.pst', steps=['cssregistry', 'jsregistry'])

        # Display duration
        self.finish()


def migrate(context):
    Migrate_To_1_0(context).run()
