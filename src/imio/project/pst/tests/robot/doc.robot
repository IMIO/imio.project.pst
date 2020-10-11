*** Settings ***
Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/selenium.robot
Resource  common.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library  plone.app.robotframework.keywords.Debugging
Library  Selenium2Screenshots

Suite Setup  Suite Setup
Suite Teardown  Close all browsers

*** Variables ***

#${BROWSER}  GoogleChrome
${BROWSER}  Firefox
${SELENIUM_RUN_ON_FAILURE}  Debug
${OS1}  etre-une-commune-qui-offre-un-service-public-moderne-efficace-et-efficient
${OS2}  etre-une-commune-ou-il-fait-bon-vivre-dans-un-cadre-agreable-propre-et-en-toute-securite
${OO}  diminuer-le-temps-dattente-de-lusager-au-guichet-population-de-20-dans-les-12-mois-a-venir
${Action}  engager-2-agents-pour-le-service-population
${task}  rediger-le-profil-de-fonction

*** Test cases ***

#1. Introduction
#1.1. Présentation générale
#1.1.1 En quoi consiste l’application ?
#1.2. Prérequis utilisateur
#1.3. Groupes et rôles prédéfinis
#1.4. Les différents éléments d’un PST
#2. Utilisation
#2.1. Premiers pas (interface_01.png)
#2.2. Consultation
#2.2.1. Visualisation du plan du PST (plan_pst.png, plan_pst_detail.png)
#2.2.2. Visualisation d’un élément (2-2-1-visualisation-pst.png, 2-2-1-visualisation-os.png, 2-2-1-visualisation-oo.png,
#       2-2-1-visualisation-action.png, 2-2-1-visualisation-tache.png)
#2.2.3. Menu de recherches prédéfinies et navigation (2-2-2-menu-recherches.png)
#2.2.4. Tableaux de bord
#2.2.4.1. Présentation générale (2-2-3-tableaux-de-bord-general.png)
#2.2.4.2. Tableau de résultat
#2.2.4.3. Filtres (2-2-3-tableaux-de-bord-filtres-avances.png)
#2.2.5. Génération de documents bureautiques (2-2-4-generation-liste-documents.png)
#2.2.5.1. Deux cas de figure se présentent lors d’une sélection d’un modèle (2-2-4-generation-document-element.png,
#         2-2-4-generation-document-tb.png)
#2.2.5.2. Liste des modèles du PST
#2.3. Modification ou création des éléments
#2.3.1. La barre d’action (barre-actions.png)
#2.3.2. Modification
#2.3.2.1. Attributs communs aux trois types d’éléments principaux
#2.3.2.2. Attributs plus spécifiques de l’objectif stratégique
#2.3.2.3. Attributs plus spécifiques de l’objectif opérationnel
#2.3.2.4. Attributs plus spécifiques de l’action (2-3-modification-financement-derniere-ligne.png,
#         2-3-modification-financement-ligne-ajoutee.png, 2-3-modification-boutons.png)
#2.3.2.5. Les attributs spéciaux
#2.3.2.5.1. Le porteur d’action (porteur.png)
#2.3.2.5.2. Les objectifs de développement durable ou ODD (odd-selection.png, odd-visu.png)
#2.3.3. Création d’un nouvel élément
#2.4. Workflow (étapes de traitement)
#2.4.1. Workflow sur les objectifs opérationnels et stratégiques
#2.4.2. Workflow sur les actions
#2.4.3. Changer d’état plus globalement
#2.5. Gestion de tâches
#2.5.1. Principe et ajout
#2.5.1.1. Principe
#2.5.1.2. Ajout d’une tâche (2-5-1-tache-ajout-vierge.png, 2-5-1-tache-ajout-complete.png, 2-5-1-tache-ajout-to-assign.png)
#2.5.2. Visualisation d’une tâche
#2.5.2.1. Sur une action (2-5-2-tache-dans-action.png)
#2.5.2.2. Dans le tableau de bord (2-5-2-tache-dans-tableau.png)
#3. Configuration du PST
#3.1. Gestion des utilisateurs
#3.2. Options sur le PST
#3.3. Gestion des contacts (3-3-annuaire.png, 3-3-mon-organisation.png, 3-3-mes-services.png, 3-3-configuration-site.png,
#     3-3-lien-config-services.png, 3-3-config-services.png, 3-3-groupes-plone.png)
#3.4. Archivage du PST
#3.4.1. Procédure (archiver-pst.png)
#3.4.2. Caractéristiques
#3.5. Options de configuration avancées (congig-site.png, gestion_config.png)
#3.5.1. Affichage des attributs sur les éléments (affichage-attr.png)
#3.5.2. Configuration de la globalisation des budgets (config-globalisation.png)
#4. Guides pas à pas
#4.1. Utilisateur
#4.1.1. Se connecter (se-connecter.png)
#4.1.2. Réinitialiser son mot de passe (mdp-oublie.png, mdp-envoye.png, mdp-reinit.png)
#4.1.2.1. Que faire si ça échoue ?
#4.2. Gestionnaire d’action
#4.3. Encodeur du PST
#4.4. Administrateur du PST
#4.4.1. Supprimer des annexes (folder-content.png)
#5. Interopérabilité (boutons.png, ecran-envoi.png, ecran-envoi-complete.png, envoi-realise.png, point-ia-delib.png
#5.1. Lien avec la gestion des délibérations (01-bouton.png, 02-ecran-envoi.jpg, 03-ecran-envoi-complete.jpg,
#     04-envoi-realise.jpg)
#5.2. Lien vers eComptes (ecompte-export.png, ecompte-import.png)
#6. Foire aux questions
#6.1. Utilisation
#6.2. Configuration
#6.3. Vous rencontrez un problème ?
#7. Journal des modifications
#7.1. Version majeure 1.3

Premiers pas
# partie 2.1 Premiers pas
    Go to  ${PLONE_URL}
    Sleep  0.3
    Capture and crop page screenshot  doc/utilisation/2-1 accès à l'application.png  css=.site-plone  id=portal-footer-wrapper
    Enable autologin as  psteditor
    #Log in  encodeur  Project69!
    Go to  ${PLONE_URL}
    Sleep  0.3
    Capture and crop page screenshot  doc/utilisation/2-1 page d'accueil.png  id=portal-header  css=.documentDescription
    Capture and crop page screenshot  doc/utilisation/2-1 fil d'ariane.png  id=breadcrumbs-you-are-here  id=breadcrumbs-home

Visualisation
# partie 2.2.1 Visualisation d'un élément
    Enable autologin as  pstreader
    Set autologin username  pstreader
    Go to  ${PLONE_URL}/pst
    Wait until element is visible  css=.faceted-table-results  10
    Sleep  0.3
    Capture and crop page screenshot  doc/utilisation/2-2-1 visualisation pst.png  css=.site-plone  id=portal-footer-wrapper
    Go to  ${PLONE_URL}/pst/${OS1}
    Wait until element is visible  css=.faceted-table-results  10
    Sleep  0.3
    Capture and crop page screenshot  doc/utilisation/2-2-1 visualisation os.png  css=.site-plone  id=portal-column-content
    Go to  ${PLONE_URL}/pst/${OS1}/${OO}
    Wait until element is visible  css=.faceted-table-results  10
    Sleep  0.3
    Capture and crop page screenshot  doc/utilisation/2-2-1 visualisation oo.png  css=.site-plone  id=portal-column-content
    Go to  ${PLONE_URL}/pst/${OS1}/${OO}/${Action}
    Wait until element is visible  css=.table_faceted_results  10
    Sleep  0.3
    Capture and crop page screenshot  doc/utilisation/2-2-1 visualisation action.png  css=.site-plone  id=portal-column-content
    Enable autologin as  agent
    Set autologin username  agent
    Go to  ${PLONE_URL}/pst/${OS1}/${OO}/${Action}
    Wait until element is visible  css=.faceted-table-results  10
    Sleep  0.3
    Capture and crop page screenshot  doc/utilisation/2-2-1 visualisation action2.png  css=.site-plone  id=portal-column-content
    Go to  ${PLONE_URL}/pst/${OS1}/${OO}/${Action}/${task}
    Wait until element is visible  formfield-form-widgets-ITask-due_date  10
    Sleep  0.3
    Capture and crop page screenshot  doc/utilisation/2-2-1 visualisation tache.png  css=.site-plone  id=portal-column-content

Menu courrier
# partie 2.2.2 Menu de recherches prédéfinies
    Enable autologin as  Manager
    Set autologin username  psteditor
    Go to  ${PLONE_URL}/pst
    Wait until element is visible  css=.faceted-table-results  10
    Sleep  0.3
    Capture and crop page screenshot  doc/utilisation/2-2-2 menu recherches.png  css=.portletWidgetCollection
    Go to  ${PLONE_URL}/pst/${OS1}/${OO}/${Action}
    Wait until element is visible  css=.faceted-table-results  10
    Sleep  0.3
    Capture and crop page screenshot  doc/utilisation/2-2-2 navigation.png  css=.portletNavigationTree

Tableaux de bord
# partie 2.2.3 Tableaux de bord
    Enable autologin as  Manager
    Set autologin username  psteditor
    Go to  ${PLONE_URL}/pst
    Wait until element is visible  css=.faceted-table-results  10
    Select collection  pst/operationalobjectives/all
    Capture and crop page screenshot  doc/utilisation/2-2-3 tableaux de bord général.png  id=content
    Click element  css=.faceted-sections-buttons-more
    Wait until element is visible  id=top---advanced---widgets  10
    Sleep  1
    Capture and crop page screenshot  doc/utilisation/2-2-3 tableaux de bord filtres avances.png  id=top---advanced---widgets
    # Go to  ${PLONE_URL}/filtre_add.png
    # Sleep  1
    # Capture and crop page screenshot  doc/utilisation/2-2-3 tableaux de bord filtres avances icone.png  css=body img

Génération de documents
# partie 2.2.4 Génération de documents
    Enable autologin as  Manager
    Set autologin username  psteditor
    Go to  ${PLONE_URL}/pst
    Wait until element is visible  css=.faceted-table-results  10
    Capture and crop page screenshot  doc/utilisation/2-2-4 génération liste documents.png  css=#viewlet-below-content-title #doc-generation-view li
    Capture and crop page screenshot  doc/utilisation/2-2-4 génération document élément.png  css=.documentFirstHeading  id=doc-generation-view
    Capture and crop page screenshot  doc/utilisation/2-2-4 génération document tb.png  css=#pst-folder-listing legend  css=.faceted-table-results thead

Modification
# partie 2.3 Modification
    Enable autologin as  psteditor
    Set autologin username  psteditor
    Go to  ${PLONE_URL}/pst/${OS2}
    Wait until element is visible  css=.faceted-table-results  10
    Sleep  0.3
    Capture and crop page screenshot  doc/utilisation/2-3 modification barre verte.png  id=viewlet-above-content  id=edit-bar  css=.documentFirstHeading
    Go to  ${PLONE_URL}/pst/${OS2}/edit
    Wait until element is visible  formfield-form-widgets-comments  10
    Sleep  0.3
    Capture and crop page screenshot  doc/utilisation/2-3 modification financement dernière ligne.png  id=formfield-form-widgets-budget
    Input text  name=form.widgets.budget.0.widgets.amount  1000
    Click element  css=#formfield-form-widgets-budget label
    Sleep  0.5
    Capture and crop page screenshot  doc/utilisation/2-3 modification financement ligne ajoutée.png  id=formfield-form-widgets-budget
    Capture and crop page screenshot  doc/utilisation/2-3 modification boutons.png  id=form-buttons-save  id=form-buttons-cancel
    Click button  id=form-buttons-cancel
    Sleep  0.3

Tâche
# partie 2.5 Ajout d'une tâche
    Enable autologin as  psteditor
    Go to  ${PLONE_URL}/pst/${OS1}/${OO}/${Action}/++add++task
    Wait until element is visible  cke_form.widgets.ITask.task_description  10
    Sleep  0.3
    Capture and crop page screenshot  doc/utilisation/2-5-1 tache ajout vierge.png  id=content
    Input text  name=form.widgets.title  Placer le CV dans notre référentiel
    Click button  id=form-buttons-save
    Sleep  0.5
    Capture and crop page screenshot  doc/utilisation/2-5-1 tache ajout complete.png  id=content
    ${UID} =  Path to uid  /${PLONE_SITE_ID}/pst/${OS1}/${OO}/${Action}/placer-le-cv-dans-notre-referentiel
    Fire transition  ${UID}  do_to_assign
    Go to  ${PLONE_URL}/pst/${OS1}/${OO}/${Action}/placer-le-cv-dans-notre-referentiel
    Wait until element is visible  css=#plone-contentmenu-workflow span.state-to_assign  10
    Capture and crop page screenshot  doc/utilisation/2-5-1 tache ajout to assign.png  id=content
# partie 2.7.2 Visualisation d'une tâche
    Go to  ${PLONE_URL}/pst/${OS1}/${OO}/${Action}
    Wait until element is visible  css=.faceted-table-results  10
    Sleep  0.5
    Capture and crop page screenshot  doc/utilisation/2-5-2 tache dans action.png  id=content
    Go to  ${PLONE_URL}/pst
    Wait until element is visible  css=.faceted-table-results  10
    Select collection  pst/tasks/all
    Wait until element is visible  css=.th_header_assigned_group  10
    Capture and crop page screenshot  doc/utilisation/2-5-2 tache dans tableau.png  id=content

Contacts
# partie 3.3 Contacts
    Enable autologin as  Manager
    Set autologin username  psteditor
    Go to  ${PLONE_URL}/pst
    Sleep  0.5
    Click element  user-name
    Wait until element is visible  css=li#personaltools-plone_setup  10
    Capture and crop page screenshot  doc/configuration/3-3 configuration site.png  id=livesearch0  css=dd.actionMenuContent
    Go to  ${PLONE_URL}/@@overview-controlpanel
    Wait until page contains  Configuration de module  10
    Update element style  css=dl.warning  display  None
    ${note50}  Add pointy note  css=.configlets li a[href$="/@@contact-plonegroup-settings"]  C'est là  position=top  color=blue
    Capture and crop page screenshot  doc/configuration/3-3 lien config services.png  css=h2:nth-of-type(2)  css=h2:nth-of-type(3)  ${note50}
    Remove element  ${note50}
    # datagridfield doesn't work in robot
    #Go to  ${PLONE_URL}/@@contact-plonegroup-settings
    #Wait until element is visible  id=pg-orga-link  10
    #Capture and crop page screenshot  doc/configuration/3-3 config services.png  id=content
    #Go to  ${PLONE_URL}/contacts
    #Wait until element is visible  css=#organizations a  10
    #Capture and crop page screenshot  doc/configuration/3-3 annuaire.png  id=portal-header  id=content
    Go to  ${PLONE_URL}/contacts/plonegroup-organization
    Wait until element is visible  css=a.addnewcontactfromorganization  10
    # Update element style  id=organization  width  400px !important
    Sleep  1
    Capture and crop page screenshot  doc/configuration/3-3 mon organisation.png  css=h1.org  css=table.templates-listing
    Go to  ${PLONE_URL}/contacts/plonegroup-organization/services
    Wait until element is visible  css=a.addnewcontactfromorganization  10
    # Update element style  id=organization  width  400px !important
    Sleep  1
    Capture and crop page screenshot  doc/configuration/3-3 mes services.png  css=h1.org  css=table.templates-listing
    Go to  ${PLONE_URL}/@@usergroup-usermembership?userid=psteditor
    Wait until element is visible  css=table.listing  10
    Capture and crop page screenshot  doc/configuration/3-3 groupes plone.png  id=content

*** Keywords ***
Suite Setup
    Open test browser
    Set Window Size  1280  4000
    Set Suite Variable  ${CROP_MARGIN}  2
    Set Selenium Implicit Wait  2
    Set Selenium Speed  0.2
    Enable autologin as  Manager
    Go to  ${PLONE_URL}/robot_init
    Disable autologin
