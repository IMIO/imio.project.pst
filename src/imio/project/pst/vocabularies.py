# -*- coding: utf-8 -*-
"""PST vocabularies."""
from collective.contact.plonegroup.browser.settings import getSelectedOrganizations
from collective.contact.plonegroup.config import get_registry_organizations
from collective.contact.plonegroup.utils import get_selected_org_suffix_users
from imio.helpers.cache import get_cachekey_volatile
from imio.project.pst import _
from imio.project.pst import EMPTY_STRING
from imio.project.pst.utils import list_wf_states
from plone import api
from plone.memoize import ram
from zope.i18n import translate
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


def voc_cache_key(method, self, context):
    return get_cachekey_volatile("%s.%s" % (self.__class__.__module__, self.__class__.__name__))


class BaseReviewStatesVocabulary(object):

    """ Incoming mail states vocabulary """

    implements(IVocabularyFactory)

    portal_type = ''

    def __call__(self, context):
        terms = []
        for state in list_wf_states(context, self.portal_type):
            terms.append(SimpleTerm(state, title=translate(state, domain='plone', context=context.REQUEST)))
        return SimpleVocabulary(terms)


class SOReviewStatesVocabulary(BaseReviewStatesVocabulary):

    portal_type = 'strategicobjective'


class OOReviewStatesVocabulary(BaseReviewStatesVocabulary):

    portal_type = 'operationalobjective'


class PSTActionReviewStatesVocabulary(BaseReviewStatesVocabulary):

    portal_type = 'pstaction'


class PSTTaskReviewStatesVocabulary(BaseReviewStatesVocabulary):

    portal_type = 'task'


class ManagerVocabulary(object):
    """ Common manager vocabulary for operational and action """
    implements(IVocabularyFactory)

    def __call__(self, context):
        return SimpleVocabulary([SimpleTerm(t[0], title=t[1]) for t in getSelectedOrganizations(first_index=2)])


class ActionCategoriesVocabularyFactory(object):
    """Provides an actions categories vocabulary"""
    implements(IVocabularyFactory)

    def __call__(self, context):
        portal_actions = api.portal.get_tool('portal_actions')

        categories = portal_actions.objectIds()
        categories.sort()
        return SimpleVocabulary(
            [SimpleTerm(cat, title=cat) for cat in categories]
        )


class ActionEditorsVocabulary(object):
    """ Provides an action editors vocabulary """
    implements(IVocabularyFactory)

    @ram.cache(voc_cache_key)
    def __call__(self, context):
        terms = []
        users = {}
        titles = []
        for uid in get_registry_organizations():
            members = get_selected_org_suffix_users(uid, ['actioneditor'])
            for member in members:
                title = member.getUser().getProperty('fullname') or member.getUserName()
                if title not in titles:
                    titles.append(title)
                    users[title] = [member]
                elif member not in users[title]:
                    users[title].append(member)
        for tit in sorted(titles):
            for mb in users[tit]:
                terms.append(SimpleTerm(mb.getMemberId(), mb.getMemberId(), tit))
#        terms.insert(0, SimpleTerm(EMPTY_STRING, EMPTY_STRING, _('Empty value')))
        return SimpleVocabulary(terms)


class EmptyActionEditorsVocabulary(object):
    """ action exitors vocabulary with empty value """
    implements(IVocabularyFactory)

    def __call__(self, context):
        voc_inst = ActionEditorsVocabulary()
        voc = voc_inst(context)
        terms = [SimpleTerm(EMPTY_STRING, EMPTY_STRING, _('Empty value'))]
        for term in voc:
            terms.append(term)
        return SimpleVocabulary(terms)
