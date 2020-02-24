# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""
from lxml.etree import XMLSyntaxError

from imio.project.pst.testing import IntegrationTestCase
from plone.z3cform.tests import TestRequest
from zope.component import getMultiAdapter

import_from_comptes = '''<?xml version="1.0" encoding="UTF-8"?>
<dataroot>
  <Identifiants>
    <Id>20180509</Id>
    <TypeAdmin>AC</TypeAdmin>
    <INS>99999</INS>
    <Type>PST</Type>
    <Exercice>2018</Exercice>
    <Version>201805V1</Version>
    <Generateur>ECOMPTES</Generateur>
  </Identifiants>
  <PST>
    <DescriptionPST>
      <IdPST>9c518ea1-fdd9-444c-b948-6a800879ffe0</IdPST>
      <Libelle>Demo PST</Libelle>
      <ExerciceDebut>2018</ExerciceDebut>
      <ExerciceFin>2022</ExerciceFin>
    </DescriptionPST>
    <Volets>
      <Volet ElementId="be4f7f34-a3f6-437e-9586-be4632bbf486" Exercice="2018">
        <Libelle>Externe</Libelle>
        <DateDebut>2018-05-09</DateDebut>
        <DateFin>2021-05-13</DateFin>
        <Description>
          <Mode>TEXTE</Mode>
          <Valeur/>
        </Description>
        <Statut>NON_COMMENCE</Statut>
        <Responsable>
          <Civilite>MADAME</Civilite>
          <Nom>Delanote</Nom>
          <Prenom>Jacqueline</Prenom>
          <Tel/>
          <eMail/>
        </Responsable>
        <Mandataire>
          <Civilite>MONSIEUR</Civilite>
          <Nom>Menfin</Nom>
          <Prenom>Gérard</Prenom>
          <Tel/>
          <eMail/>
        </Mandataire>
        <Departement>Service jeunesse</Departement>
        <TauxAvancement>0</TauxAvancement>
        <RemarqueStatut>
          <Mode>TEXTE</Mode>
          <Valeur/>
        </RemarqueStatut>
        <ETP>0</ETP>
        <Plans/>
        <Partenaires/>
        <Articles/>
        <Projections/>
        <ObjectifStrategiques>
          <ObjectifStrategique {0} Exercice="2020">
            <Libelle>Etre une administration qui développe efficacement les services administratifs pour une gestion cohérente et efficiente</Libelle>
            <DateDebut>2018-02-06</DateDebut>
            <DateFin>2020-10-15</DateFin>
            <Description>
              <Mode>TEXTE</Mode>
              <Valeur/>
            </Description>
            <Statut>NON_COMMENCE</Statut>
            <TauxAvancement>0</TauxAvancement>
            <RemarqueStatut>
              <Mode>TEXTE</Mode>
              <Valeur/>
            </RemarqueStatut>
            <ETP>0</ETP>
            <Plans/>
            <Partenaires/>
            <Articles>
                <Article>
                    <Exercice>2020</Exercice>
                    <Service>O</Service>
                    <Type>D</Type>
                    <CodeArticle>123/45678.2020</CodeArticle>
                    <Libelle>Indemnités XYZ</Libelle>
                    <Montant>1793.5</Montant>
                </Article>
                <Article>
                    <Exercice>2020</Exercice>
                    <Service>O</Service>
                    <Type>D</Type>
                    <CodeArticle>012/12145.2020</CodeArticle>
                    <Libelle>Indemnités OMC</Libelle>
                    <Montant>2020</Montant>
                </Article>
            </Articles>
            <Projections>
                <Projection>
                    <Service>O</Service>
                    <Type>R</Type>
                    <GroupeEco>61</GroupeEco>
                    <Libelle>61 Transferts</Libelle>
                    <Exercices>
                        <Exercice Valeur="2024">
                            <Montant>0</Montant>
                        </Exercice>
                        <Exercice Valeur="2023">
                            <Montant>0</Montant>
                        </Exercice>
                        <Exercice Valeur="2022">
                            <Montant>100</Montant>
                        </Exercice>
                        <Exercice Valeur="2021">
                            <Montant>100</Montant>
                        </Exercice>
                        <Exercice Valeur="2020">
                            <Montant>100</Montant>
                        </Exercice>
                        <Exercice Valeur="2019">
                            <Montant>0</Montant>
                        </Exercice>
                    </Exercices>
                </Projection>
                <Projection>
                    <Service>O</Service>
                    <Type>R</Type>
                    <GroupeEco>60</GroupeEco>
                    <Libelle>60 Prestations</Libelle>
                    <Exercices>
                        <Exercice Valeur="2024">
                            <Montant>190</Montant>
                        </Exercice>
                        <Exercice Valeur="2023">
                            <Montant>180</Montant>
                        </Exercice>
                        <Exercice Valeur="2022">
                            <Montant>170</Montant>
                        </Exercice>
                        <Exercice Valeur="2021">
                            <Montant>160</Montant>
                        </Exercice>
                        <Exercice Valeur="2020">
                            <Montant>150</Montant>
                        </Exercice>
                        <Exercice Valeur="2019">
                            <Montant>0</Montant>
                        </Exercice>
                    </Exercices>
                </Projection>
            </Projections>
            <ObjectifsOperationnels/>
          </ObjectifStrategique>
        </ObjectifStrategiques>
      </Volet>
    </Volets>
  </PST>
</dataroot>
'''


class TestEcomptes(IntegrationTestCase):
    """Test import from eComptes."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.os = self.portal.pst['etre-une-commune-qui-offre-un-service-public-moderne-efficace-et-efficient']
        self.os.analytic_budget = [
            {'comment': u'', 'article': u'123/45678.2020 - Sera supprimé', 'amount': 1000, 'year': 2020},
        ]

    def test_import_form_fails(self):
        """The imported XML is missing an attribute, so it won't be match the schema"""
        request = TestRequest()
        import_from_ecomptes_from = getMultiAdapter(
            (self.portal.pst, request),
            name=u"import_from_ecomptes",
        )
        import_from_ecomptes_from.request.form = {
            'form.widgets.ecomptes_xml': import_from_comptes.format('')}
        import_from_ecomptes_from.update()
        data, errors = import_from_ecomptes_from.extractData()
        self.assertEqual(len(errors), 0)

        with self.assertRaises(XMLSyntaxError):
            import_from_ecomptes_from.parse_xml(data)

    def test_import_form_updates(self):
        """Import a valid XML export from eComptes & update an OS analytic budget"""
        request = TestRequest()
        import_from_ecomptes_from = getMultiAdapter(
            (self.portal.pst, request),
            name=u"import_from_ecomptes",
        )
        mandatory_attribute = 'ElementId="{0}"'.format(self.os.UID())
        import_from_ecomptes_from.request.form = {
            'form.widgets.ecomptes_xml': import_from_comptes.format(mandatory_attribute)}
        import_from_ecomptes_from.update()
        data, errors = import_from_ecomptes_from.extractData()
        self.assertEqual(len(errors), 0)

        parsed_xml = import_from_ecomptes_from.parse_xml(data)
        import_from_ecomptes_from.update_pst(parsed_xml)
        self.assertEquals(
            [
                {
                    'service': 'O',
                    'title': u'Indemnit\xe9s XYZ',
                    'year': 2020,
                    'amount': 1793.5,
                    'btype': 'D',
                    'article': '123/45678.2020'
                },
                {
                    'service': 'O',
                    'title': u'Indemnit\xe9s OMC',
                    'year': 2020,
                    'amount': 2020.0,
                    'btype': 'D',
                    'article': '012/12145.2020'
                }
            ],
            self.os.analytic_budget,
        )
        self.assertEquals([
            {'group': u'61', 'service': u'O', 'title': u'61 Transferts', 'btype': u'R', 'amount': 0.0, 'year': 2024},
            {'group': u'61', 'service': u'O', 'title': u'61 Transferts', 'btype': u'R', 'amount': 0.0, 'year': 2023},
            {'group': u'61', 'service': u'O', 'title': u'61 Transferts', 'btype': u'R', 'amount': 100.0, 'year': 2022},
            {'group': u'61', 'service': u'O', 'title': u'61 Transferts', 'btype': u'R', 'amount': 100.0, 'year': 2021},
            {'group': u'61', 'service': u'O', 'title': u'61 Transferts', 'btype': u'R', 'amount': 100.0, 'year': 2020},
            {'group': u'61', 'service': u'O', 'title': u'61 Transferts', 'btype': u'R', 'amount': 0.0, 'year': 2019},
            {'group': u'60', 'service': u'O', 'title': u'60 Prestations', 'btype': u'R', 'amount': 190.0, 'year': 2024},
            {'group': u'60', 'service': u'O', 'title': u'60 Prestations', 'btype': u'R', 'amount': 180.0, 'year': 2023},
            {'group': u'60', 'service': u'O', 'title': u'60 Prestations', 'btype': u'R', 'amount': 170.0, 'year': 2022},
            {'group': u'60', 'service': u'O', 'title': u'60 Prestations', 'btype': u'R', 'amount': 160.0, 'year': 2021},
            {'group': u'60', 'service': u'O', 'title': u'60 Prestations', 'btype': u'R', 'amount': 150.0, 'year': 2020},
            {'group': u'60', 'service': u'O', 'title': u'60 Prestations', 'btype': u'R', 'amount': 0.0, 'year': 2019}
        ], self.os.projection)
