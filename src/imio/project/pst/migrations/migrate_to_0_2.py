# ------------------------------------------------------------------------------
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

    def run(self):
        logger.info('Migrating to imio.project.pst 0.2...')

        self._addFileTypeToProjectSpaceConstrainedTypes()
        # reinstall so changes on allowed_content_types are taken into account
        self.reinstall(profiles=[u'profile-imio.project.pst:default', ])
        self.finish()


def migrate(context):
    '''This migration function:

       1) We want to be able to add 'Files' in the 'pst' projectspace.;
       2) Reinstall.
    '''
    Migrate_To_0_2(context).run()
