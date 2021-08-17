# -*- coding: utf-8 -*-

import logging

import transaction
from Products.CMFPlone.interfaces import ISelectableConstrainTypes
from collective.documentgenerator.utils import update_oo_config
from collective.iconifiedcategory.utils import calculate_category_id
from collective.messagesviewlet.utils import add_message
from imio.helpers.content import create
from imio.migrator.migrator import Migrator
from imio.project.core.content.project import IProject
from imio.project.core.content.projectspace import IProjectSpace
from imio.project.pst.data import get_main_templates
from imio.project.pst.data import get_styles_templates
from imio.project.pst.data import get_templates
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
    context_vars = template.context_variables
    if context_var not in context_vars:
        context_vars.append(context_var)


class Migrate_To_1_3_2(Migrator):

    def __init__(self, context):
        Migrator.__init__(self, context)

    def run(self):
        # check if oo port must be changed
        update_oo_config()

        # override templates
        self.runProfileSteps('imio.project.pst', steps=['imioprojectpst-override-templates'], profile='update',
                             run_dependencies=False)

        # upgrade all except 'imio.project.pst:default'. Needed with bin/upgrade-portals
        # self.upgradeAll(omit=['imio.project.pst:default'])

        # for prod in []:
        #     mark_last_version(self.portal, product=prod)

        # Reorder css and js
        self.runProfileSteps('imio.project.pst', steps=['cssregistry', 'jsregistry'], run_dependencies=False)

        # Add a new-version warning message in message config
        self.add_new_version_message()

        # Handle budget comment <NO_VALUE> by setting None
        self.migrate_budget()

        # Add new templates
        update_templates()

        # Add new context variable in detail template
        add_context_var('detail', {'name': u'without_oo_fields', 'value': u','})

        # Migrate annex File in Annex content
        self.migrate_annex()

        # Display duration
        self.finish()

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
            self.runProfileSteps('imio.project.pst', steps=['typeinfo'], run_dependencies=False)
            qi.installProduct('imio.annex')
            brains = self.catalog(object_provides=IProjectSpace.__identifier__)
            for brain in brains:
                pstprojectspace = brain.getObject()
                behaviour = ISelectableConstrainTypes(pstprojectspace)
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
                                          'pstaction', 'pstsubaction']:
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


def migrate(context):
    Migrate_To_1_3_2(context).run()
