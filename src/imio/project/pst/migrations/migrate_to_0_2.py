# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('imio.project.pst')

from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes

from imio.migrator.migrator import Migrator


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
        logger.info('Done.')

    def run(self):
        logger.info('Migrating to imio.project.pst 0.2...')

        # reinstall first so changes on allowed_content_types are taken into account
        self.reinstall(profiles=[u'profile-imio.project.pst:default', ])
        # now do specific migration
        self._addFileTypeToProjectSpaceConstrainedTypes()
        self._initNewFields()
        self.finish()


def migrate(context):
    '''This migration function:

       1) We want to be able to add 'Files' in the 'pst' projectspace;
       2) Initialize new fields for existing objects;
       3) Reinstall.
    '''
    Migrate_To_0_2(context).run()
