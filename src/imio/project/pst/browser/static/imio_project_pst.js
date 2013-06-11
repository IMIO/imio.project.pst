/* change the datagridfields main table class from 'datagridwidget-table-view' to 'listing' */
function replaceDataGridFieldsTableClass(){
jQuery(function($) {
$('table.datagridwidget-table-view').each(function(){
    $(this).attr('class', 'listing');
    /* add class 'odd' on first TR, the one used for datagridfield table header */
    $(this.tHead).children('TR').attr('class', 'odd')
    })
})
}
replaceDataGridFieldsTableClass()