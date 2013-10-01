# -*- coding: utf-8 -*-

from zope.component import getUtility
from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes

from imio.migrator.migrator import Migrator
from imio.project.core.events import _updateParentsBudgetInfos
import logging
logger = logging.getLogger('imio.project.pst')


class Migrate_To_0_2(Migrator):
    def __init__(self, context):
        Migrator.__init__(self, context)

    def _addFileTypeToProjectSpaceConstrainedTypes(self):
        """We want to be able to add 'Files' in the 'pst' projectspace."""
        logger.info("Adding 'File' to constrained types of projectspace 'pst'...")
        projectspace = self.portal.pst
        # we do not publish because, in published state, editors cannot more modify
        # do_transitions(projectspace, transitions=['publish_internally'], logger=logger)
        # set locally allowed types
        behaviour = ISelectableConstrainTypes(projectspace)
        behaviour.setConstrainTypesMode(1)
        behaviour.setLocallyAllowedTypes(['strategicobjective', 'File', ])
        behaviour.setImmediatelyAddableTypes(['strategicobjective', 'File', ])
        logger.info('Done.')

    def _initNewFields(self):
        """Initialize the PST projectspace budget_types field and
           budget/budget_details fields on OO, OS, Action."""
        logger.info("Initializing new fields...")
        projectspace = self.portal.pst
        from types import NoneType
        if isinstance(projectspace.budget_types, NoneType):
            budget_types = [
                {'label': u"Europe",
                 'key': "europe"},
                {'label': u"Fédéral",
                 'key': "federal"},
                {'label': u"Wallonie",
                 'key': "wallonie"},
                {'label': u"Fédération Wallonie-Bruxelles",
                 'key': "federation-wallonie-bruxelles"},
                {'label': u"Province",
                 'key': "province"},
                {'label': u"Ville",
                 'key': "ville"},
                {'label': u"Autres",
                 'key': "autres"},
            ]
            projectspace.budget_types = budget_types
        else:
            # migration already done
            logger.info('Already done.')
            return
        brains = self.portal.portal_catalog(portal_type=['strategicobjective',
                                                         'operationalobjective',
                                                         'pstaction', ])
        for brain in brains:
            obj = brain.getObject()
            # old value of 'budget' is now moved to 'budget_comments' and field
            # 'budget' is now an empty datagridfield
            obj.budget_comments = obj.budget
            obj.budget = []
            if obj.budget_comments is not None and isinstance(obj.budget_comments, str):
                obj.budget_comments = obj.budget_comments.decode('utf8')
            if obj.observation is not None and isinstance(obj.observation, str):
                obj.observation = obj.observation.decode('utf8')
            if obj.portal_type == 'pstaction' and obj.work_plan is not None and isinstance(obj.work_plan, str):
                obj.work_plan = obj.work_plan.decode('utf8')
        logger.info('Done.')

    def _updateBudgetInfosAnnotations(self):
        """Update annotations regarding budgetInfos."""
        logger.info("Updating budgetinfos annotations...")
        brains = self.portal.portal_catalog(portal_type=['strategicobjective',
                                                         'operationalobjective',
                                                         'pstaction', ])
        for brain in brains:
            obj = brain.getObject()
            _updateParentsBudgetInfos(obj)
        logger.info('Done.')

    def _updateContactPlonegroupConfiguration(self):
        """ Update plonegroup configuration """
        logger.info("Updating plonegroup configuration...")
        from collective.contact.plonegroup.config import ORGANIZATIONS_REGISTRY
        from plone.registry.interfaces import IRegistry
        registry = getUtility(IRegistry)
        if not registry[ORGANIZATIONS_REGISTRY]:
            path = '%s/contacts/plonegroup-organization/services' % '/'.join(self.portal.getPhysicalPath())
            brains = self.portal.portal_catalog(portal_type=['organization'],
                                                path={"query": path},
                                                sort_on='sortable_title')
            registry[ORGANIZATIONS_REGISTRY] = [brain.UID for brain in brains]
        logger.info("Done.")

    def _updateManagerField(self):
        """ Update manager field """
        logger.info("Updating manager field.")
        from zope.component import getMultiAdapter
        group_uids = {}
        path = '%s/contacts/plonegroup-organization/services' % '/'.join(self.portal.getPhysicalPath())

        def store_group_uids(pc, levels):
            brains = pc(portal_type=['organization'],
                        path={"query": '/'.join(levels), "depth": 1},
                        sort_on='sortable_title')
            for brain in brains:
                next_levels = levels + [brain.id]
                org_id = "-".join(next_levels[1:])
                if org_id in group_uids.keys():
                    logger.error("'id' already exists" % org_id)
                group_uids[org_id] = '%s_actioneditor' % brain.UID
                if len(levels) <= 2:
                    store_group_uids(pc, next_levels)

        store_group_uids(self.portal.portal_catalog, [path])

        brains = self.portal.portal_catalog(portal_type=['operationalobjective',
                                                         'pstaction', ])
        for brain in brains:
            obj = brain.getObject()
            #logger.info("-> %s" % '/'.join(obj.getPhysicalPath()))
            new_managers = []
            for id in obj.manager:
                try:
                    new_managers.append(group_uids[id])
                except KeyError:
                    logger.warn("Old manager value '%s' not in group" % id)
            edit = getMultiAdapter((obj, obj.REQUEST), name=u'edit')

            class Dummy(object):
                def __init__(self, context):
                    self.context = context

            # needed to avoid invalid attribute in BudgetTypeVocabulary class
            obj.REQUEST['PUBLISHED'] = Dummy(obj)
            # form fields and widgets update
            edit.form_instance.update()
            # save "extracted data"
            edit.form_instance.applyChanges({'manager': new_managers})
        logger.info('Done.')

    def _replaceProjectWorkflow(self):
        """ Replace the project workflow by new ones """
        from plone.app.workflow.remap import remap_workflow
        # pstaction
        mapping = {'created': 'created', 'ongoing': 'ongoing', 'stopped': 'stopped', 'terminated': 'terminated',
                   'to_be_scheduled': 'to_be_scheduled'}
        remap_workflow(self.context, ['pstaction'], ['pst_action_workflow'], state_map=mapping)
        # objectives
        mapping = {'created': 'created', 'ongoing': 'ongoing', 'stopped': 'achieved', 'terminated': 'achieved',
                   'to_be_scheduled': 'ongoing'}
        remap_workflow(self.context, ['strategicobjective', 'operationalobjective'], ['pst_objective_workflow'],
                       state_map=mapping)

    def run(self):
        logger.info('Migrating to imio.project.pst 0.2...')

        # reinstall first so changes on allowed_content_types are taken into account
        self.reinstall(profiles=[u'profile-imio.project.pst:default', ])
        # We want to be able to add 'Files' in the 'pst' projectspace;
        self._addFileTypeToProjectSpaceConstrainedTypes()
        # Initialize new fields for existing objects;
        self._initNewFields()
        # Update budgetInfos related annotations
        self._updateBudgetInfosAnnotations()
        # Update contact plonegroup configuration
        self._updateContactPlonegroupConfiguration()
        # Update manager field of operationalobjective and pstaction
        self._updateManagerField()
        # Replace the project_workflow by new ones
        self._replaceProjectWorkflow()
        # update portal_catalog as icons are no more defined on the portal_type
        self.refreshDatabase()
        # Display duration
        self.finish()


def migrate(context):
    '''
    '''
    Migrate_To_0_2(context).run()
