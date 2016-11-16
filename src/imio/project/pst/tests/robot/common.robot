*** Keywords ***

## Actions

Select collection
    [Documentation]  Click element of the collection widget corresponding to given path
    [Arguments]  ${col_path}  ${results}=1  ${widget_name}=c1  ${old_css_element}=#content h1.documentFirstHeading
    # Test if current page is already a faceted form
    ${passed} = 	Run Keyword And Return Status 	Page should contain element  faceted-form
    Run Keyword If 	${passed} 	Assign id to element  css=${old_css_element}  temporary-id-to-be-sure-page-is-changed
    ${UID} =  Path to uid  /${PLONE_SITE_ID}/${col_path}
    Click element  ${widget_name}${UID}
    Wait until element is not visible  temporary-id-to-be-sure-page-is-changed
    Run keyword if  '${results}'=='1'  Wait until element is visible  css=.faceted-table-results  10  ELSE  Wait until element is visible  css=.table_faceted_no_results  10
    Sleep  0.5
#    [Return]  ${UID}
