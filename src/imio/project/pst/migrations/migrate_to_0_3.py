# -*- coding: utf-8 -*-

from collective.contact.plonegroup.config import ORGANIZATIONS_REGISTRY
from collective.contact.plonegroup.config import FUNCTIONS_REGISTRY

from imio.helpers.catalog import addOrUpdateIndexes
from imio.migrator.migrator import Migrator
from imio.project.core.content.project import IProject
from imio.project.core.content.projectspace import IProjectSpace
from imio.project.core.utils import getProjectSpace

import logging

from Products.CMFPlone.utils import base_hasattr
from plone import api

from zope.component import getUtility
from plone.registry.interfaces import IRegistry

logger = logging.getLogger('imio.project.pst')


class Migrate_To_0_3(Migrator):
    def __init__(self, context):
        Migrator.__init__(self, context)

    def perform_reference_number(self):
        """
        Add or update the reference_number index
        compute the reference_number per projectspace
        store the last_reference_number in projectspace
        update catalog
        """
        logger.info('Perform reference number ...')
        addOrUpdateIndexes(self.context, {'reference_number': ('FieldIndex', {})})
        catalog = api.portal.get_tool('portal_catalog')
        projectspaces = catalog(object_provides=IProjectSpace.__identifier__)
        for projectspace in projectspaces:
            path = '/'.join(self.portal.getPhysicalPath()) + '/' + projectspace.id
            brains = catalog(object_provides=IProject.__identifier__, path={'query': path, 'depth': 3}, sort_on='created')
            for num, brain in enumerate(brains):
                obj = brain.getObject()
                if obj.reference_number == 0:
                    obj.reference_number = num + 1
                    obj.reindexObject(['reference_number'])
                    projectspace = getProjectSpace(obj)
                    projectspace.last_reference_number = num + 1

        logger.info('Done.')

    def update_administrative_responsible_vocabulary(self):
        """
        """
        logger.info('Update administrative responsible vocabulary ...')
        catalog = api.portal.get_tool('portal_catalog')
        oos = catalog(portal_type="operationalobjective")
        registry = getUtility(IRegistry)
        functions_id = [fct_dic['fct_id'] for fct_dic in registry[FUNCTIONS_REGISTRY]]
        groups = []
        for uid in registry[ORGANIZATIONS_REGISTRY]:
            for fct_id in functions_id:
                groups.append("%s_%s" % (uid, fct_id))
        for oo in oos:
            obj = oo.getObject()
            contacts = obj.contacts
            organisation = getattr(contacts, 'plonegroup-organization')
            services = organisation.services
            res = []
            for adm_resp in obj.administrative_responsible:
                if adm_resp.endswith('_actioneditor'):
                    #Already updated
                    res.append(adm_resp)
                else:
                    service = getattr(services, adm_resp, None)
                    if not service:
                        #May be two levels organizations
                        import ipdb; ipdb.set_trace()
                        combs = dual_split_combination(adm_resp, '-')
                        found = False
                        for comb in combs:
                            service_level1 = getattr(services, comb[0], None)
                            if service_level1:
                                service_level2 = getattr(service_level1, comb[1], None)
                                if service_level2:
                                    found = True
                                    service_uid = service_level2.UID()
                                    adm_resp = service_uid + '_actioneditor'
                                    if adm_resp not in groups:
                                        #Config missing
                                        logger.info(
                                                'Title : ' + service.title +
                                                'Group : ' + adm_resp +
                                                ' NOT FOUND IN PLONE GROUPS'
                                        )
                                    else:
                                        res.append(adm_resp)
                                break
                        if not found:
                            logger.info(adm_resp + ' NOT FOUND IN SERVICES NODE')
                    else:
                        service_uid = service.UID()
                        adm_resp = service_uid + '_actioneditor'
                        if adm_resp not in groups:
                            #Config missing
                            logger.info(
                                    'Title : ' + service.title +
                                    'Group : ' + adm_resp +
                                    ' NOT FOUND IN PLONE GROUPS'
                            )
                        else:
                            res.append(adm_resp)
            obj.administrative_responsible = res
        logger.info('Done.')

    def run(self):
        self.perform_reference_number()
        self.update_administrative_responsible_vocabulary()
        # reinstall
        self.reinstall(profiles=[u'profile-imio.project.pst:default', ])
        # Display duration
        self.finish()


def migrate(context):
    Migrate_To_0_3(context).run()


def dual_split_combination(string, separator):
    L = string.split(separator)
    COMBS = []

    for i, e in enumerate(L[:len(L)-1]):
        duo = []
        BEGIN = ""
        END = ""
        for j, e in enumerate(L[:i+1]):
            if j == 0:
                BEGIN = e
            else:
                BEGIN = BEGIN + '-' + e
                print BEGIN
        for j, e in enumerate(L[i+1:]):
            if j == 0:
                END = e
            else:
                END = END + '-' + e
        duo.append(BEGIN)
        duo.append(END)
        COMBS.append(duo)
    return COMBS
