# -*- coding: utf-8 -*-

import logging

import transaction
from Products.CMFPlone.interfaces import ISelectableConstrainTypes
from collective.documentgenerator.utils import update_oo_config
from collective.iconifiedcategory.utils import calculate_category_id
from collective.messagesviewlet.utils import add_message
from collective.task.behaviors import ITask
from imio.helpers.content import create, richtextval
from imio.migrator.migrator import Migrator
from imio.project.core.content.project import IProject
from imio.project.core.content.projectspace import IProjectSpace
from imio.project.pst.data import get_main_templates
from imio.project.pst.data import get_styles_templates
from imio.project.pst.data import get_templates
from imio.project.pst.setuphandlers import _ as _translate, reimport_faceted_config
from imio.project.pst.setuphandlers import configure_iconified_category
from plone import api
from plone.app.contenttypes.interfaces import IFile

logger = logging.getLogger('imio.project.pst')


def update_templates():
    """Add new templates"""
    cids = create(get_styles_templates())
    cids.update(create(get_main_templates(cids)))
    cids.update(create(get_templates(cids)))


def add_context_var(template_id, context_var):
    template = getattr(api.portal.get().templates, template_id)
    if not template.context_variables:
        template.context_variables = []
    if context_var not in template.context_variables:
        template.context_variables.append(context_var)


def migrate_context_var():
    template_vars = {
        'ddetail': [{'name': u'without_oo_fields', 'value': u','}],
        'ddetail-all': [{'name': u'without_oo_fields', 'value': u','}],
        'ddetail-tasks': [{'name': u'without_oo_fields', 'value': u','}],
        'ddetail-tasks-all': [{'name': u'without_oo_fields', 'value': u','}],
        'detail': [{'name': u'without_oo_fields', 'value': u','}],
        'detail-all': [{'name': u'without_oo_fields', 'value': u','}],
        'detail-tasks': [{'name': u'without_oo_fields', 'value': u','}],
        'detail-tasks-all': [{'name': u'without_oo_fields', 'value': u','}],
        'dexport': [{'name': u'with_tasks', 'value': u''}],
        'dfollow-all': [{'name': u'option_0', 'value': u'1'}, {'name': u'option_1', 'value': u''}],
        'dfollow-tasks': [{'name': u'option_0', 'value': u'1'}, {'name': u'option_1', 'value': u''}],
        'dfollow-tasks-all': [{'name': u'option_0', 'value': u'1'}, {'name': u'option_1', 'value': u''}],
        'export': [{'name': u'with_tasks', 'value': u''}],
        'follow-all': [{'name': u'option_0', 'value': u'1'}, {'name': u'option_1', 'value': u''}],
        'follow-tasks': [{'name': u'option_0', 'value': u'1'}, {'name': u'option_1', 'value': u''}],
        'follow-tasks-all': [{'name': u'option_0', 'value': u'1'}, {'name': u'option_1', 'value': u''}],
    }
    for template_id in template_vars:
        for context_var in template_vars[template_id]:
            add_context_var(template_id, context_var)


class Migrate_To_1_3_2(Migrator):

    def __init__(self, context):
        Migrator.__init__(self, context)

    def run(self):
        # check if oo port must be changed
        # update_oo_config()

        # override templates
        self.runProfileSteps('imio.project.pst', steps=['imioprojectpst-update-templates'], profile='update',
                             run_dependencies=False)

        # Import catalog tool's
        self.runProfileSteps('imio.project.pst', steps=['catalog'], profile='default',
                             run_dependencies=False)
        # upgrade all except 'imio.project.pst:default'. Needed with bin/upgrade-portals
        # self.upgradeAll(omit=['imio.project.pst:default'])

        # for prod in []:
        #     mark_last_version(self.portal, product=prod)

        # Reorder css and js
        # self.runProfileSteps('imio.project.pst', steps=['cssregistry', 'jsregistry'], run_dependencies=False)

        # Add a backport warning message in message config
        self.add_backport_message()

        # Handle budget comment <NO_VALUE> by setting None
        # self.migrate_budget()

        # Add new templates
        # update_templates()

        # Migrate context variable
        # migrate_context_var()

        # Migrate annex File in Annex content
        # self.migrate_annex()

        # Migrate to text/x-html-safe
        # self.migrate_to_text_x_html_safe()

        # Update front_page
        # self.update_front_page()

        # reindex all projects spaces, projects and tasks
        # self.reindex_some_types()

        # Updated dashboard config
        self.update_dashboard_criterias()

        # Display duration
        self.finish()

    def add_backport_message(self):
        msgs_to_del = ('new-version', 'doc', 'new-dashboard')
        for msg_to_del in msgs_to_del:
            if msg_to_del in self.portal['messages-config']:
                api.content.delete(self.portal['messages-config'][msg_to_del])
        add_message(
            'backport',
            'Mise à jour',
            u'<p>Votre instance a été mise à jour !</p>'
            u'<p>La <a href="https://docs.imio.be/imio-doc/ia.pst/fonctionnalites/index.html#version-1-3-2" target="_blank">'
            u'documentation</a> a également été mise à jour avec les nouvelles fonctionnalités</a>.</p>',
            msg_type='warning',
            can_hide=True,
            req_roles=['Authenticated'],
            activate=True
        )

    def add_new_version_message(self):
        if 'new-version' in self.portal['messages-config']:
            api.content.delete(self.portal['messages-config']['new-version'])
        if 'new-dashboard' in self.portal['messages-config']:
            api.content.delete(self.portal['messages-config']['new-dashboard'])
        add_message(
            'new-version',
            'Version 1.3.2',
            u'<p>Vous êtes passés à la version d\'iA.PST 1.3.2 !</p>'
            u'<p>La <a href="https://docs.imio.be/imio-doc/ia.pst/" target="_blank">'
            u'documentation</a> a été mise à jour et comporte une nouvelle section sur les fonctionnalités</a>.</p>',
            msg_type='warning',
            can_hide=True,
            req_roles=['Authenticated'],
            activate=True
        )

    def add_new_dashboard_message(self):
        if 'new-version' in self.portal['messages-config']:
            api.content.delete(self.portal['messages-config']['new-version'])
        if 'new-dashboard' not in self.portal['messages-config']:
            add_message(
                'new-dashboard',
                'Nouveau modèle de tableau de bord',
                u'<p>Votre instance a été mise à jour avec <a href="https://docs.imio.be/imio-doc/ia.pst/'
                u'fonctionnalites/nouveau_modele_tableau_bord.html" target="_blank">une nouvelle fonctionnalité</a>.'
                u'</p>',
                msg_type='warning',
                can_hide=True,
                req_roles=['Authenticated'],
                activate=True
            )

    def migrate_budget(self):
        brains = self.catalog(object_provides=IProject.__identifier__)
        for brain in brains:
            budget = brain.getObject().budget
            if budget:
                for budget_line in budget:
                    budget_line['budget_comment'] = None

    def migrate_annex(self):
        qi = self.context.portal_quickinstaller
        if not qi.isProductInstalled('imio.annex'):
            qi.installProduct('imio.annex')
        self.runProfileSteps('imio.project.pst', steps=['typeinfo'], run_dependencies=False)
        brains = self.catalog(object_provides=IProjectSpace.__identifier__)
        for brain in brains:
            pst_obj = brain.getObject()
            behaviour = ISelectableConstrainTypes(pst_obj)
            behaviour.setConstrainTypesMode(1)
            behaviour.setLocallyAllowedTypes(['strategicobjective', 'annex', ])
            behaviour.setImmediatelyAddableTypes(['strategicobjective', 'annex', ])
        portal = api.portal.get()
        configure_iconified_category(portal)
        annexTypeId = calculate_category_id(portal.categorization.annexes.get('annexes-pst'))
        brains = self.catalog(object_provides=IFile.__identifier__)
        for brain in brains:
            file_obj = brain.getObject()
            parent = file_obj.aq_parent
            if parent.portal_type in ['pstprojectspace', 'strategicobjective', 'operationalobjective',
                                      'pstaction', 'pstsubaction', 'task']:
                annexId = file_obj.id
                api.content.delete(obj=parent[annexId])
                api.content.create(
                    container=parent,
                    type='annex',
                    id=annexId,
                    title=file_obj.Title(),
                    description=file_obj.Description(),
                    content_category=annexTypeId,
                    file=file_obj.file,
                )
                transaction.commit()

    def reindex_some_types(self):
        brains = self.catalog(object_provides=IProjectSpace.__identifier__)
        for brain in brains:
            brain.getObject().reindexObject()
        brains = self.catalog(object_provides=IProject.__identifier__)
        for brain in brains:
            brain.getObject().reindexObject()
        brains = self.catalog(object_provides=ITask.__identifier__)
        for brain in brains:
            brain.getObject().reindexObject()

    def migrate_to_text_x_html_safe(self):
        """Migrate richtext's outputMimeType to text/x-html-safe."""
        for brain in self.catalog(object_provides='imio.project.core.content.project.IProject'):
            obj = brain.getObject()
            if obj.budget_comments:
                if obj.budget_comments.outputMimeType == 'text/html':
                    obj.budget_comments = richtextval(obj.budget_comments.raw)
                    obj.reindexObject()
            if obj.observation:
                if obj.observation.outputMimeType == 'text/html':
                    obj.observation = richtextval(obj.observation.raw)
                    obj.reindexObject()
            if obj.comments:
                if obj.comments.outputMimeType == 'text/html':
                    obj.comments = richtextval(obj.comments.raw)
                    obj.reindexObject()

    def update_front_page(self):
        frontpage = getattr(self.portal, 'front-page')
        frontpage.title = _translate("front_page_title")
        frontpage.reindexObject()

    def update_dashboard_criterias(self):
        for brain in self.catalog(object_provides='imio.project.pst.interfaces.IImioPSTProject'):
            pst = brain.getObject()
            mapping = {
                'strategicobjectives': 'strategicobjective',
                'operationalobjectives': 'operationalobjective',
                'pstactions': 'pstaction',
            }
            for col_folder_id, content_type in mapping.iteritems():
                col_folder = pst[col_folder_id]
                reimport_faceted_config(col_folder, xml='{}.xml'.format(content_type),
                                        default_UID=col_folder['all'].UID())

def migrate(context):
    Migrate_To_1_3_2(context).run()
