# -*- coding: utf-8 -*-

from collective.documentgenerator.utils import update_oo_config
from collective.messagesviewlet.utils import add_message
from eea.facetednavigation.criteria.interfaces import ICriteria
from eea.facetednavigation.subtypes.interfaces import IFacetedNavigable
from eea.facetednavigation.widgets.storage import Criterion
from imio.migrator.migrator import Migrator
from imio.project.core.content.projectspace import IProjectSpace
from imio.project.pst.content.action import IPSTAction
from plone import api
from plone.app.contenttypes.migration.dxmigration import migrate_base_class_to_new_class
from plone.registry.interfaces import IRegistry
from Products.CPUtils.Extensions.utils import mark_last_version
from zope.component import getUtility

import logging

logger = logging.getLogger('imio.project.pst')


class Migrate_To_1_3_1(Migrator):

    def __init__(self, context):
        Migrator.__init__(self, context)

    def run(self):
        # check if oo port must be changed
        update_oo_config()

        self.runProfileSteps('imio.project.pst', steps=['actions', 'catalog'], run_dependencies=False)

        # migrate projectspace in pstprojectspace
        self.migrate_projectspace_in_pstprojectspace()

        # Assigning new custom ecomptes permissions to role
        self.manage_permission()

        # update daterange criteria
        self.update_dashboards()

        # remove configlets
        self.remove_configlets()

        # Allowed webservices on subactions
        self.migrate_webservices_config()

        # reindex all actions
        self.reindex_all_actions()

        # upgrade all except 'imio.project.pst:default'. Needed with bin/upgrade-portals
        self.upgradeAll(omit=['imio.project.pst:default'])

        # for prod in []:
        #     mark_last_version(self.portal, product=prod)

        # Reorder css and js
        self.runProfileSteps('imio.project.pst', steps=['cssregistry', 'jsregistry'], run_dependencies=False)

        # Add a new-version warning message in message config
        self.add_new_version_message()

        # Display duration
        self.finish()

    def add_plan_to_lists_fields(self, *lists_fields):
        for list_fields in lists_fields:
            if 'plan' not in list_fields:
                if 'categories' in list_fields:
                    list_fields.insert(list_fields.index('categories') + 1, 'plan')
                else:
                    list_fields.append('plan')

    def migrate_pst_fields(self, field_list):
        updated_list = []
        if field_list:
            for field_name in field_list:
                updated_list.append({
                    'field_name': field_name,
                    'read_tal_condition': '',
                    'write_tal_condition': '',
                })
        return updated_list

    def update_dashboards(self):
        # update daterange criteria
        brains = api.content.find(object_provides=IFacetedNavigable.__identifier__, portal_type='Folder')
        for brain in brains:
            obj = brain.getObject()
            criterion = ICriteria(obj)
            for key, criteria in criterion.items():
                if criteria.get("widget") != "daterange":
                    continue
                if criteria.get("usePloneDateFormat") is True:
                    continue
                logger.info("Upgrade daterange widget for faceted {0}".format(obj))
                position = criterion.criteria.index(criteria)
                values = criteria.__dict__
                values["usePloneDateFormat"] = True
                values["labelStart"] = u'Start date'
                values["labelEnd"] = u'End date'
                criterion.criteria[position] = Criterion(**values)
                criterion.criteria._p_changed = 1

    def migrate_projectspace_in_pstprojectspace(self):
        plan_values = [
            {'label': u"Agenda 21 local",
             'key': "agenda-21-local"},
            {'label': u"PCA Plan communal d'Aménagement",
             'key': "pca-plan-communal-d-amenagement"},
            {'label': u"Plan communal d'Urgence",
             'key': "plan-communal-d-urgence"},
            {'label': u"Plan communal de développement de la nature PCDN",
             'key': "plan-communal-de-developpement-de-la-nature-pcdn"},
            {'label': u"Plan communal de développement rural (PCDR)",
             'key': "plan-communal-de-developpement-rural-pcdn"},
            {'label': u"Plan d'ancrage communal",
             'key': "plan-d-ancrage-communal"},
            {'label': u"Plan de cohésion social (PCS)",
             'key': "plan-de-cohesion-social-pcs"},
            {'label': u"Plan de formation du personnel",
             'key': "plan-de-formation-du-personnel"},
            {'label': u"Plan de gestion",
             'key': "plan-de-gestion"},
            {'label': u"Plan de mobilité",
             'key': "plan-de-mobilite"},
            {'label': u"Plan global de prévention",
             'key': "plan-global-de-prevention"},
            {'label': u"Plan zonal de sécurité",
             'key': "plan-zonal-de-securite"},
            {'label': u"Schémas de développement commercial",
             'key': "schemas-de-developpement-commercial"},
        ]

        so_bdg_states = ['ongoing', 'achieved']
        oo_bdg_states = ['ongoing', 'achieved']
        a_bdg_states = ['ongoing', 'terminated', 'to_be_scheduled']

        registry = getUtility(IRegistry)
        prj_fld_record = registry.get('imio.project.settings.project_fields')
        so_record = registry.get('imio.project.settings.strategicobjective_fields')
        oo_record = registry.get('imio.project.settings.operationalobjective_fields')
        a_record = registry.get('imio.project.settings.pstaction_fields')
        sa_record = registry.get('imio.project.settings.pstsubaction_fields')
        if so_record and oo_record and a_record and sa_record:
            self.add_plan_to_lists_fields(so_record, oo_record, a_record)
            self.runProfileSteps('imio.project.pst', steps=['typeinfo'], profile='default',
                                 run_dependencies=False)
            projectspace_brains = self.catalog(object_provides=IProjectSpace.__identifier__)
            if projectspace_brains[0].getObject().__class__.__name__ == 'ProjectSpace':
                for projectspace_brain in projectspace_brains:
                    projectspace_obj = projectspace_brain.getObject()
                    migrate_base_class_to_new_class(
                        projectspace_obj,
                        new_class_name='imio.project.pst.content.pstprojectspace.PSTProjectSpace')
                    # projectspace is now pstprojectspace
                    projectspace_obj.portal_type = 'pstprojectspace'
                    projectspace_obj.project_fields = self.migrate_pst_fields(prj_fld_record)
                    projectspace_obj.strategicobjective_fields = self.migrate_pst_fields(so_record)
                    projectspace_obj.operationalobjective_fields = self.migrate_pst_fields(oo_record)
                    projectspace_obj.pstaction_fields = self.migrate_pst_fields(a_record)
                    projectspace_obj.pstsubaction_fields = self.migrate_pst_fields(sa_record)
                    if not getattr(projectspace_obj, 'plan_values'):
                        setattr(projectspace_obj, 'plan_values', plan_values)
                    if not getattr(projectspace_obj, 'strategicobjective_budget_states'):
                        setattr(projectspace_obj, 'strategicobjective_budget_states', so_bdg_states)
                    if not getattr(projectspace_obj, 'operationalobjective_budget_states'):
                        setattr(projectspace_obj, 'operationalobjective_budget_states', oo_bdg_states)
                    if not getattr(projectspace_obj, 'pstaction_budget_states'):
                        setattr(projectspace_obj, 'pstaction_budget_states', a_bdg_states)
                    if not getattr(projectspace_obj, 'pstsubaction_budget_states'):
                        setattr(projectspace_obj, 'pstsubaction_budget_states', a_bdg_states)

                del registry.records['imio.project.settings.project_fields']
                del registry.records['imio.project.settings.strategicobjective_fields']
                del registry.records['imio.project.settings.operationalobjective_fields']
                del registry.records['imio.project.settings.pstaction_fields']
                del registry.records['imio.project.settings.pstsubaction_fields']

    def manage_permission(self):
        self.portal.manage_permission('imio.project.pst: ecomptes import',
                                      ('Manager', 'Site Administrator', 'Contributor'), acquire=0)
        self.portal.manage_permission('imio.project.pst: ecomptes export',
                                      ('Manager', 'Site Administrator', 'Contributor'), acquire=0)

    def remove_configlets(self):
        config_tool = api.portal.get_tool('portal_controlpanel')
        config_tool.unregisterConfiglet('imio.project.core.settings')
        config_tool.unregisterConfiglet('imio.project.pst.settings')

    def migrate_webservices_config(self):
        """Add pstsbaction to webservice TAL condition."""
        registry = getUtility(IRegistry)
        generated_actions = registry.get('imio.pm.wsclient.browser.settings.IWS4PMClientSettings.generated_actions')
        if generated_actions:
            for action in generated_actions:
                if action['condition'] == u"python: context.getPortalTypeName() in ('pstaction', 'task')":
                    action['condition'] = u"python: context.getPortalTypeName() in ('pstaction', 'pstsubaction', 'task')"
                else:
                    logger.warning("Settings for WS4PM client: generated_actions was not updated ! "
                                   "Current value'{}'".format(action))
            api.portal.set_registry_record('imio.pm.wsclient.browser.settings.IWS4PMClientSettings.generated_actions',
                                           generated_actions)

    def reindex_all_actions(self):
        actions_brains = self.catalog(object_provides=IPSTAction.__identifier__)
        for action_brain in actions_brains:
            action_brain.getObject().reindexObject()

    def add_new_version_message(self):
        if 'new-version' in self.portal['messages-config']:
            api.content.delete(self.portal['messages-config']['new-version'])
        add_message(
            'new-version',
            'Version 1.3.1',
            u'<p>Vous êtes passés à la version d\'iA.PST 1.3.1 !</p>'
            u'<p>La <a href="https://docs.imio.be/imio-doc/ia.pst/" target="_blank">'
            u'documentation</a> a été mise à jour et comporte une nouvelle section sur les nouveautés</a>.</p>',
            msg_type='warning',
            can_hide=True,
            req_roles=['Authenticated'],
            activate=True
        )


def migrate(context):
    Migrate_To_1_3_1(context).run()
