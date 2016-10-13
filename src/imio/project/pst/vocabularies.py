# -*- coding: utf-8 -*-
"""PST vocabularies."""
from zope.i18n import translate
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from collective.contact.plonegroup.browser.settings import getSelectedOrganizations
from imio.project.pst.utils import list_wf_states


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
