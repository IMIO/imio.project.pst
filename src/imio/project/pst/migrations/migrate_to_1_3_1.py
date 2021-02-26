# -*- coding: utf-8 -*-

import logging

from collective.documentgenerator.utils import update_oo_config
from collective.messagesviewlet.utils import add_message
from dexterity.localroles.utils import add_fti_configuration
from eea.facetednavigation.criteria.interfaces import ICriteria
from eea.facetednavigation.subtypes.interfaces import IFacetedNavigable
from eea.facetednavigation.widgets.storage import Criterion
from imio.helpers.content import richtextval
from imio.migrator.migrator import Migrator
from imio.project.core.content.project import IProject
from imio.project.core.content.projectspace import IProjectSpace
from imio.project.pst.content.action import IPSTAction
from imio.project.pst.content.pstprojectspace import IPSTProjectSpace
from plone import api
from plone.app.contenttypes.migration.dxmigration import migrate_base_class_to_new_class
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

logger = logging.getLogger('imio.project.pst')


def migrate_pst_fields(field_list):
    updated_list = []
    if field_list:
        for field_name in field_list:
            updated_list.append({
                'field_name': field_name,
                'read_tal_condition': '',
                'write_tal_condition': '',
            })
    return updated_list


def update_dashboards():
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


def add_plan_to_lists_fields(*lists_fields):
    for list_fields in lists_fields:
        if 'plan' not in list_fields:
            if 'categories' in list_fields:
                list_fields.insert(list_fields.index('categories') + 1, 'plan')
            else:
                list_fields.append('plan')


def remove_configlets():
    config_tool = api.portal.get_tool('portal_controlpanel')
    config_tool.unregisterConfiglet('imio.project.core.settings')
    config_tool.unregisterConfiglet('imio.project.pst.settings')


def migrate_webservices_config():
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


class Migrate_To_1_3_1(Migrator):

    def __init__(self, context):
        Migrator.__init__(self, context)

    def run(self):
        # check if oo port must be changed
        update_oo_config()

        self.runProfileSteps('imio.project.pst', steps=['actions', 'catalog'], run_dependencies=False)

        # migrate projectspace in pstprojectspace
        self.migrate_projectspace_in_pstprojectspace()

        self.enable_categories_column_on_action_dashboard()

        # Assigning new custom ecomptes permissions to role
        self.manage_permission()

        # update daterange criteria
        update_dashboards()

        # remove configlets
        remove_configlets()

        # Allowed webservices on subactions
        migrate_webservices_config()

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

        # Use safe_html
        self.migrate_projects_richtextvalues()

        # Display duration
        self.finish()

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

        strategicobjective_columns = [
            u'select_row', u'pretty_link', u'review_state',
            u'categories', u'ModificationDate', u'history_actions']
        operationalobjective_columns = [
            u'select_row', u'pretty_link', u'parents', u'review_state',
            u'manager', u'planned_end_date', u'priority', u'categories',
            u'sdgs', u'ModificationDate', u'history_actions']
        pstaction_columns = [
            u'select_row', u'pretty_link', u'parents', u'review_state',
            u'manager', u'responsible', u'planned_begin_date', u'planned_end_date',
            u'effective_begin_date', u'effective_end_date', u'progress',
            u'health_indicator', u'categories', u'sdgs', u'ModificationDate',
            u'history_actions']
        tasks_columns = [
            u'select_row', u'pretty_link', u'parents', u'review_state',
            u'assigned_group', u'assigned_user', u'due_date', u'CreationDate',
            u'ModificationDate', u'history_actions']

        registry = getUtility(IRegistry)
        prj_fld_record = registry.get('imio.project.settings.project_fields')
        so_record = registry.get('imio.project.settings.strategicobjective_fields')
        oo_record = registry.get('imio.project.settings.operationalobjective_fields')
        a_record = registry.get('imio.project.settings.pstaction_fields')
        sa_record = registry.get('imio.project.settings.pstsubaction_fields')
        if so_record and oo_record and a_record and sa_record:
            add_plan_to_lists_fields(so_record, oo_record, a_record)
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
                    projectspace_obj.project_fields = migrate_pst_fields(prj_fld_record)
                    projectspace_obj.strategicobjective_fields = migrate_pst_fields(so_record)
                    projectspace_obj.operationalobjective_fields = migrate_pst_fields(oo_record)
                    projectspace_obj.pstaction_fields = migrate_pst_fields(a_record)
                    projectspace_obj.pstsubaction_fields = migrate_pst_fields(sa_record)
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
                    if not getattr(projectspace_obj, 'strategicobjectives_columns'):
                        setattr(projectspace_obj, 'strategicobjectives_columns', strategicobjective_columns)
                    if not getattr(projectspace_obj, 'operationalobjectives_columns'):
                        setattr(projectspace_obj, 'operationalobjectives_columns', operationalobjective_columns)
                    if not getattr(projectspace_obj, 'pstactions_columns'):
                        setattr(projectspace_obj, 'pstactions_columns', pstaction_columns)
                    if not getattr(projectspace_obj, 'tasks_columns'):
                        setattr(projectspace_obj, 'tasks_columns', tasks_columns)
                    add_fti_configuration('pstprojectspace',
                                          {'internally_published': {'pst_readers': {'roles': ['Reader']}}},
                                          keyname='static_config', force=False)

                del registry.records['imio.project.settings.project_fields']
                del registry.records['imio.project.settings.strategicobjective_fields']
                del registry.records['imio.project.settings.operationalobjective_fields']
                del registry.records['imio.project.settings.pstaction_fields']
                del registry.records['imio.project.settings.pstsubaction_fields']

    def enable_categories_column_on_action_dashboard(self):
        act_dbs = self.catalog(portal_type="Folder",
                               object_provides="imio.project.pst.interfaces.IActionDashboardBatchActions")
        for db in act_dbs:
            for brain in self.catalog.searchResults({'path': {'query': db.getPath()},
                                                     'portal_type': 'DashboardCollection'}):
                col = brain.getObject()
                if u'categories' not in col.customViewFields:
                    nl = list(col.customViewFields)
                    nl.insert(col.customViewFields.index(u'sdgs'), u'categories')
                    col.customViewFields = tuple(nl)
        brains = self.catalog(object_provides=IPSTProjectSpace.__identifier__)
        for brain in brains:
            pst = brain.getObject()
            if 'categories' not in pst.pstactions_columns:
                if 'sdgs' in pst.pstactions_columns:
                    pst.pstactions_columns.insert(pst.pstactions_columns.index('sdgs'), 'categories')
                else:
                    pst.pstactions_columns.append('categories')

    def manage_permission(self):
        self.portal.manage_permission('imio.project.pst: ecomptes import',
                                      ('Manager', 'Site Administrator', 'Contributor'), acquire=0)
        self.portal.manage_permission('imio.project.pst: ecomptes export',
                                      ('Manager', 'Site Administrator', 'Contributor'), acquire=0)

    def reindex_all_projects(self):
        brains = self.catalog(object_provides=IProject.__identifier__)
        for brain in brains:
            brain.getObject().reindexObject()

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

    def migrate_projects_richtextvalues(self):
        project_brains = self.catalog(object_provides=IProject.__identifier__)
        for project_brain in project_brains:
            for field_name in ['budget_comments', 'observation', 'comments']:
                project_obj = project_brain.getObject()
                field_value = getattr(project_obj, field_name)
                if field_value:
                    setattr(project_obj, field_name, richtextval(field_value.raw))


def migrate(context):
    Migrate_To_1_3_1(context).run()
