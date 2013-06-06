# -*- coding: utf-8 -*-

from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from plone.dexterity.schema import DexteritySchemaPolicy

from imio.project.core.content.project import IProject
from imio.project.core.content.project import Project


class IStrategicObjective(IProject):
    """
        StrategicObjective schema, field ordering
    """


class StrategicObjective(Project):
    """ """
    implements(IStrategicObjective)


class StrategicObjectiveSchemaPolicy(DexteritySchemaPolicy):
    """ """

    def bases(self, schemaName, tree):
        return (IStrategicObjective, )


class CategoryVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        """"""
        terms = []
        terms.append(
            SimpleTerm(u"Volet interne : Administration générale - Accessibilité de l'Administration",
                       u"volet-interne-adm-generale-accessibilite-administration",
                       u"Volet interne : Administration générale - Accessibilité de l'Administration"))
        terms.append(
            SimpleTerm(u"Volet interne : Administration générale - Structure de pilotage de l'Administration",
                       u"volet-interne-adm-generale-structure-pilotage-administration",
                       u"Volet interne : Administration générale - Structure de pilotage de l'Administration"))
        terms.append(
            SimpleTerm(u"Volet interne : Administration générale - Gestion des ressources humaines",
                       u"volet-interne-adm-generale-gestion-ressources-humaines",
                       u"Volet interne : Administration générale - Gestion des ressources humaines"))
        terms.append(
            SimpleTerm(u"Volet interne : Administration générale - Structuration des services",
                       u"volet-interne-adm-generale-structuration-services",
                       u"Volet interne : Administration générale - Structuration des services"))
        terms.append(
            SimpleTerm(u"Volet interne : Administration générale - Fonctionnement propre à chacun des services",
                       u"volet-interne-adm-generale-fonctionnement-propre-chacun-services",
                       u"Volet interne : Administration générale - Fonctionnement propre à chacun des services"))
        terms.append(
            SimpleTerm(u"Volet interne : Administration générale - Processus et simplification administrative",
                       u"volet-interne-adm-generale-processus-simplification-administrative",
                       u"Volet interne : Administration générale - Processus et simplification administrative"))
        terms.append(
            SimpleTerm(u"Volet interne : Administration générale - Communication interne",
                       u"volet-interne-adm-generale-communication-interne",
                       u"Volet interne : Administration générale - Communication interne"))
        terms.append(
            SimpleTerm(u"Volet interne : Administration générale - Gestion du patrimoine",
                       u"volet-interne-adm-generale-gestion-patrimoine",
                       u"Volet interne : Administration générale - Gestion du patrimoine"))
        terms.append(
            SimpleTerm(u"Volet interne : Administration générale - Gestion informatique et Egouvernement",
                       u"volet-interne-adm-generale-gestion-informatique-egouvernement",
                       u"Volet interne : Administration générale - Gestion informatique et Egouvernement"))
        terms.append(
            SimpleTerm(u"Volet interne : Administration générale - Synergie avec d'autres institutions publiques",
                       u"volet-interne-adm-generale-synergie-autres-institutions-publiques",
                       u"Volet interne : Administration générale - Synergie avec d'autres institutions publiques"))
        terms.append(
            SimpleTerm(u"Volet externe : Développement des politiques - Action sociale",
                       u"volet-externe-dvp-politiques-action-sociale",
                       u"Volet externe : Développement des politiques - Action sociale"))
        terms.append(
            SimpleTerm(u"Volet externe : Développement des politiques - Aménagement du territoire",
                       u"volet-externe-dvp-politiques-amenagement-territoire",
                       u"Volet externe : Développement des politiques - Aménagement du territoire"))
        terms.append(
            SimpleTerm(u"Volet externe : Développement des politiques - Culture",
                       u"volet-externe-dvp-politiques-culture",
                       u"Volet externe : Développement des politiques - Culture"))
        terms.append(
            SimpleTerm(u"Volet externe : Développement des politiques - Développement économique",
                       u"volet-externe-dvp-politiques-dvp-economique",
                       u"Volet externe : Développement des politiques - Développement économique"))
        terms.append(
            SimpleTerm(u"Volet externe : Développement des politiques - Egouvernement",
                       u"volet-externe-dvp-politiques-egouvernement",
                       u"Volet externe : Développement des politiques - Egouvernement"))
        terms.append(
            SimpleTerm(u"Volet externe : Développement des politiques - Energie",
                       u"volet-externe-dvp-politiques-energie",
                       u"Volet externe : Développement des politiques - Energie"))
        terms.append(
            SimpleTerm(u"Volet externe : Développement des politiques - Environnement",
                       u"volet-externe-dvp-politiques-environnement",
                       u"Volet externe : Développement des politiques - Environnement"))
        terms.append(
            SimpleTerm(u"Volet externe : Développement des politiques - Internationnal",
                       u"volet-externe-dvp-politiques-internationnal",
                       u"Volet externe : Développement des politiques - Internationnal"))
        terms.append(
            SimpleTerm(u"Volet externe : Développement des politiques - Logement",
                       u"volet-externe-dvp-politiques-logement",
                       u"Volet externe : Développement des politiques - Logement"))
        terms.append(
            SimpleTerm(u"Volet externe : Développement des politiques - Mobilité",
                       u"volet-externe-dvp-politiques-mobilite",
                       u"Volet externe : Développement des politiques - Mobilité"))
        terms.append(
            SimpleTerm(u"Volet externe : Développement des politiques - Propreté et sécurité publique",
                       u"volet-externe-dvp-politiques-proprete-securite-publique",
                       u"Volet externe : Développement des politiques - Propreté et sécurité publique"))
        terms.append(
            SimpleTerm(u"Volet externe : Développement des politiques - Sport",
                       u"volet-externe-dvp-politiques-sport",
                       u"Volet externe : Développement des politiques - Sport"))
        terms.append(
            SimpleTerm(u"Volet externe : Développement des politiques - Tourisme",
                       u"volet-externe-dvp-politiques-tourisme",
                       u"Volet externe : Développement des politiques - Tourisme"))
        return SimpleVocabulary(terms)
