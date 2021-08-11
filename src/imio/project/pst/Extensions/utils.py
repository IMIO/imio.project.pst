# -*- coding: utf-8 -*-

from collective.contact.plonegroup.config import FUNCTIONS_REGISTRY
from collective.contact.plonegroup.config import ORGANIZATIONS_REGISTRY
from imio.project.pst import add_path
from plone import api
from Products.CPUtils.Extensions.utils import check_zope_admin
from Products.CPUtils.Extensions.utils import log_list

import os


def update_templates(self):
    """
        update pst templates
    """
    templates = [
        #('pstaction_template', 'fichepstaction.odt'),
        #('operationalobjective_template', 'ficheoo.odt'),
        ('pst_template', 'pst_full.odt'),
        #('status_template', 'tableaubord.odt'),
    ]
    out = []
    folder = self.templates
    templates_dir = add_path('profiles/default/templates')
    for id, filename in templates:
        filename_path = os.path.join(templates_dir, filename)
        try:
            f = open(filename_path, 'rb')
            file_content = f.read()
            f.close()
        except:
            continue
        out.append("Template '%s' updated with '%s'" % (id, filename))
        new_template = getattr(folder, id)
        new_template.setFile(file_content)
        new_template.setFilename(filename)
        new_template.setFormat("application/vnd.oasis.opendocument.text")
    return '\n'.join(out)


def clean_examples(self):
    """ Clean created examples """
    if not check_zope_admin():
        return "You must be a zope manager to run this script"
    out = []
    portal = api.portal.getSite()
    portal.portal_properties.site_properties.enable_link_integrity_checks = False

    # Delete os
    brains = api.content.find(portal_type='strategicobjective', path='/'.join(portal.pst.getPhysicalPath()))
    for brain in brains:
        log_list(out, "Deleting os '%s'" % brain.getPath())
        api.content.delete(obj=brain.getObject(), check_linkintegrity=False)

    portal.pst.last_reference_number = 0

    # Deactivate own organizations
    ownorg = portal['contacts']['plonegroup-organization']
    brains = api.content.find(context=ownorg, portal_type='organization',
                              id=['plonegroup-organization', 'echevins', '1er-echevin', 'services', 'accueil'])
    kept_orgs = [brain.UID for brain in brains]
    log_list(out, "Activating only 'accueil'")
    api.portal.set_registry_record(name=ORGANIZATIONS_REGISTRY, value=[ownorg['services']['accueil'].UID()])
    # Delete organization
    brains = api.content.find(context=ownorg, portal_type='organization', sort_on='path', sort_order='descending')
    for brain in brains:
        uid = brain.UID
        if uid in kept_orgs:
            continue
        log_list(out, "Deleting organization '%s'" % brain.getPath())
        api.content.delete(obj=brain.getObject(), check_linkintegrity=False)
    # Delete users
    for userid in ['psteditor', 'pstreader', 'chef', 'agent']:
        user = api.user.get(userid=userid)
        if user:
            for brain in api.content.find(Creator=userid, sort_on='path', sort_order='descending'):
                log_list(out, "Deleting object '%s' created by '%s'" % (brain.getPath(), userid))
                api.content.delete(obj=brain.getObject(), check_linkintegrity=False)
            for group in api.group.get_groups(user=user):
                if group.id == 'AuthenticatedUsers':
                    continue
                log_list(out, "Removing user '%s' from group '%s'" % (userid, group.getProperty('title')))
                api.group.remove_user(group=group, user=user)
            log_list(out, "Deleting user '%s'" % userid)
            api.user.delete(user=user)
    # Delete groups
    functions = [dic['fct_id'] for dic in api.portal.get_registry_record(FUNCTIONS_REGISTRY)]
    groups = api.group.get_groups()
    for group in groups:
        if '_' not in group.id or group.id in ['pst_editors', 'pst_readers']:
            continue
        parts = group.id.split('_')
        if len(parts) == 1:
            continue
        org_uid = parts[0]
        function = '_'.join(parts[1:])
        if org_uid in kept_orgs or function not in functions:
            continue
        log_list(out, "Deleting group '%s'" % group.getProperty('title'))
        api.group.delete(group=group)
    portal.portal_properties.site_properties.enable_link_integrity_checks = True
    return '\n'.join(out)
