# -*- coding: utf-8 -*-
"""Init and utils."""

from AccessControl.Permissions import delete_objects
from plone import api
from plone.dexterity.content import Container
from Products.CMFPlone.PloneFolder import BasePloneFolder
from zope.component import queryUtility
from zope.i18n.interfaces import ITranslationDomain
from zope.i18nmessageid import MessageFactory

import os


_ = MessageFactory('imio.project.pst')

PRODUCT_DIR = os.path.dirname(__file__)
ASSIGNED_USER_FUNCTIONS = ['editeur', 'validateur']
EMPTY_STRING = '__empty_string__'
# Value added in the CKeditor menuStyles to specify that it has been customized
CKEDITOR_MENUSTYLES_CUSTOMIZED_MSG = '/* Styles have been customized, do not remove this line! */'


def initialize(context):
    """Initializer called when used as a Zope 2 product."""


def add_path(path):
    path = path.strip('/ ')
    return "%s/%s" % (PRODUCT_DIR, path)

# We modify the protection ('Delete objects' permission) on container manage_delObjects method
# Normally to delete an item, user must have the delete permission on the item and on the parent container
# Now container 'manage_delObjects' method is protected by roles (Member)
# Based on what is done in AccessControl.class_init
for klass in (BasePloneFolder, Container):
    new = []
    for perm in klass.__ac_permissions__:
        if perm[0] == delete_objects:
            if len(perm[1]) > 1:
                methods = list(perm[1])
                methods.remove('manage_delObjects')
                perm[1] = tuple(methods)
            else:
                continue
        new.append(perm)
    klass.__ac_permissions__ = tuple(new)
    klass.manage_delObjects__roles__ = ('Authenticated', 'Member')


def _tr(msgid, domain='imio.project.pst', mapping={}):
    translation_domain = queryUtility(ITranslationDomain, domain)
    sp = api.portal.get().portal_properties.site_properties
    return translation_domain.translate(msgid, target_language=sp.getProperty('default_language', 'fr'),
                                        mapping=mapping)
