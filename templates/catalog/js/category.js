// Open modal window to edit category
{% if perms.catalog.change_category %}
$("body").delegate("[data-do='open-edit-category']", "click", function(){

    $.post('/catalog/ajax/get/category/', {
        id: $(this).data('category-id'),
        csrfmiddlewaretoken: '{{ csrf_token }}'
    },
    function(data) {
        if ('success' == data.status){

            $('#modal-edit-category-header').text('Редактирование категории');

            $('#edit-category-id').val(data['category']['id']);
            $('#edit-category-name').val(data['category']['name']);
            $('#edit-category-alias').val(data['category']['alias']);
            if (data['category']['parent']) {
                $('#edit-category-parent').val(data['category']['parent']['id']);
            } else {
                $('#edit-category-parent').val(0);
            }
            $('#edit-category-description').val(data['category']['description']);
            $('#edit-category-state').prop('checked', data['category']['state']);

            $('#modal-edit-category').foundation('open');
        }
    }, "json");

    return false;
});
{% endif %}

// Open modal window to add category
{% if perms.catalog.add_category %}
$("body").delegate("[data-do='open-new-category']", "click", function(){

    $('#modal-edit-category-header').text('Новая категория');

    $('#edit-category-id').val('0');
    $('#edit-category-name').val('');
    $('#edit-category-alias').val('');
    $('#edit-category-parent').val('0');
    $('#edit-category-description').val('');
    $('#edit-category-state').prop('checked', false);

    $('#modal-edit-category').foundation('open');

    return false;
});
{% endif %}

// Save category
{% if perms.catalog.change_category %}
$("body").delegate("[data-do='edit-category-save']", "click", function(){

    $.post('/catalog/ajax/save/category/', {
        id: $('#edit-category-id').val(),
        name: $('#edit-category-name').val(),
        alias: $('#edit-category-alias').val(),
        parent_id: $('#edit-category-parent').val(),
        description: $('#edit-category-description').val(),
        state: $('#edit-category-state').prop('checked'),
        csrfmiddlewaretoken: '{{ csrf_token }}'
    },
    function(data) {

        if ('success' == data.status){

            $('[data-category-name="' + data['category']['id'] + '"]').text(data['category']['name_leveled']);
            $('[data-category-state="' + data['category']['id'] + '"]').prop('checked', data['category']['state']);

            $('#edit-category-id').val('0');
            $('#edit-category-name').val('');
            $('#edit-category-alias').val('');
            $('#edit-category-parent').val('');
            $('#edit-category-description').val('');
            $('#edit-category-state').prop('checked', false);

            if (true == data.reload){
                setTimeout(function () {location.reload();}, 3000);
            }

            $('#modal-edit-category').foundation('close');
        }
    }, "json");

    return false;
});
{% endif %}

// Cancel Edit Category
{% if perms.catalog.change_category %}
$("body").delegate("[data-do='edit-category-cancel']", "click", function(){

    $('#edit-category-id').val('0');
    $('#edit-category-name').val('');
    $('#edit-category-alias').val('');
    $('#edit-category-parent').val('0');
    $('#edit-category-description').val('');
    $('#edit-category-state').prop('checked', false);

    $('#modal-edit-category').foundation('close');

    return false;
});
{% endif %}

// Open delete Category window
{% if perms.catalog.delete_category %}
$("body").delegate("[data-do='open-delete-category']", "click", function(){

    $.post('/catalog/ajax/get/category/', {
        id: $(this).data('category-id'),
        csrfmiddlewaretoken: '{{ csrf_token }}'
    },
    function(data) {
        if ('success' == data.status){

            $('#delete-category-id').val(data['category']['id']);
            $('#delete-category-name').text(data['category']['name'])

            $('#modal-delete-category').foundation('open');
        }
    }, "json");

    return false;
});
{% endif %}


// Delete Category
{% if perms.catalog.delete_category %}
$("body").delegate("[data-do='delete-category-apply']", "click", function(){

    $.post('/catalog/ajax/delete/category/', {
        id: $('#delete-category-id').val(),
        csrfmiddlewaretoken: '{{ csrf_token }}'
    },
    function(data) {
        if ('success' == data.status) {

            $('[data-category="' + data['id'] + '"]').empty();

            $('#modal-delete-category').foundation('close');
        }
    }, "json");

    return false;
});
{% endif %}

// Cancel delete Category
{% if perms.catalog.delete_category %}
$("body").delegate("[data-do='delete-category-cancel']", "click", function(){

    $('#delete-category-id').val(0);

    $('#modal-delete-category').foundation('close');

    return false;
});
{% endif %}


// Switch State
{% if perms.catalog.change_category %}
$("body").delegate("[data-do='switch-category-state']", "click", function(){

    $.post('/catalog/ajax/switch-state/category/', {
        id: $(this).data('category-id'),
        state: $(this).prop('checked'),
        csrfmiddlewaretoken: '{{ csrf_token }}'
    },
    function(data) {
        if ('success' == data.status) {
            return false;
        } else {
            return true;
        }
    }, "json");

    return true;
});
{% endif %}
