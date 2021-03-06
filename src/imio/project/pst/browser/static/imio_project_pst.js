$(document).ready(function(){
    $('#formfield-form-widgets-organizations .formHelp').before('<span id="pg-orga-link"><a href="contacts/plonegroup-organization" target="_blank">Lien vers mon organisation</a></span>');

    $("#form-widgets-budget_split .cell-2 input").attr("readonly", "readonly");

    $('.sitemap_jstree').jstree({
        types: {
            "default": {
                draggable: false,
                renameable: false,
                deletable: false,
                creatable: false
            }
        },

        ui : {
            dots: false,
            selected_parent_close: false
        },

        callback: {
            onload: function(tree) {
                var searchParams = new URLSearchParams(window.location.search);
                if (searchParams.has("came_from")) {
                    var came_from = searchParams.get("came_from");
                    var came_from_node = $("#" + came_from);

                    came_from_node.css("font-weight", "bold");

                    tree.open_all(came_from_node); // develop children of came_from

                    tree.toggle_branch(came_from_node); // develop came_from node

                    var parent = tree.parent(came_from_node);
                    while (parent !== -1) {
                        tree.open_branch(parent);  // develop parent(s) of came_from node
                        parent = tree.parent(parent);
                    }

                } else {
                    tree.open_all();
                }

                $("#deploy_sitemap").on("click", function() {
                    tree.open_all();
                });


                $("#collapse_sitemap").on("click", function() {
                    tree.close_all();
                });

                $("#colorize").on("click", function() {
                    $("ul.sitemap_jstree li a").each(function(){
                        $(this).toggleClass($(this).attr('data-state'));
                    });
                });

            },

            onselect: function (node, tree) {
                window.open(node.firstElementChild.href, "_blank");
            }
        }
    });
});
