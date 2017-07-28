{% if perms.catalog.add_vendor %}
$("body").delegate("[data-do='open-new-vendor']", "click", function(){

	$('#modal-edit-vendor-header').text('Добавить производителя');

	$('#edit-vendor-id').val('0');
	$('#edit-vendor-name').val('');
	$('#edit-vendor-alias').val('');
	$('#edit-vendor-description').val('');
	$('#edit-vendor-state').prop('checked', true);

	$('#modal-edit-vendor').foundation('open');

	return false;
});
{% endif %}


{% if perms.catalog.change_vendor %}
$("body").delegate("[data-do='open-edit-vendor']", "click", function(){

	$.post('/catalog/ajax/get/vendor/', {
		id: $(this).data('vendor-id'),
		csrfmiddlewaretoken: '{{ csrf_token }}'
	},
	function(data) {
		if ('success' == data.status){

			$('#modal-edit-vendor-header').text('Редактировать производителя');

			$('#edit-vendor-id').val(data['vendor']['id']);
			$('#edit-vendor-name').val(data['vendor']['name']);
			$('#edit-vendor-alias').val(data['vendor']['alias']);
			$('#edit-vendor-description').val(data['vendor']['description']);
			$('#edit-vendor-state').prop('checked', data['vendor']['state']);

			$('#modal-edit-vendor').foundation('open');
		}
	}, "json");

	return false;
});
{% endif %}


{% if perms.catalog.change_vendor %}
$("body").delegate("[data-do='edit-vendor-save']", "click", function(){

	$.post('/catalog/ajax/save/vendor/', {
		id: $('#edit-vendor-id').val(),
		name: $('#edit-vendor-name').val(),
		alias: $('#edit-vendor-alias').val(),
		description: $('#edit-vendor-description').val(),
		state: $('#edit-vendor-state').prop('checked'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {

		if ('success' == data.status){

			$('[data-vendor-name="' + data['vendor']['id'] + '"]').text(data['vendor']['name']);
			$('[data-vendor-state="' + data['vendor']['id'] + '"]').prop('checked', data['vendor']['state']);

			$('#edit-vendor-id').val('0');
			$('#edit-vendor-name').val('');
			$('#edit-vendor-alias').val('');
			$('#edit-vendor-description').val('');
			$('#edit-vendor-state').prop('checked', false);

			$('#modal-edit-vendor').foundation('close');
		}
	}, "json");

	return false;
});
{% endif %}

{% if perms.catalog.change_vendor %}
$("body").delegate("[data-do='edit-vendor-cancel']", "click", function(){

	$('#edit-vendor-id').val('0');
	$('#edit-vendor-name').val('');
	$('#edit-vendor-alias').val('');
	$('#edit-vendor-description').val('');
	$('#edit-vendor-state').prop('checked', false);

	$('#modal-edit-vendor').foundation('close');

	return false;
});
{% endif %}


// TODO
{% if perms.catalog.change_vendor %}

// Отключаем автоматическую отправку формы при вводе
$('link-vendor-id').keypress(function (e) {
    var key = e.which;
    if(key == 13) {
        return false;
    }
});

$("body").delegate("[data-do='open-link-vendor']", "click", function(){
	$.post('/catalog/ajax/get/vendor/', {
		id: $(this).data('vendor-id'),
		csrfmiddlewaretoken: '{{ csrf_token }}'
	},
	function(data) {
		if ('success' == data.status){

			$('#link-vendor-id').val(data['vendor']['id']);

            // Подставляем имя вендора или вендора, на которого он ссылается
            if (data['vendor']['double']){
                $('#link-vendor-name').val(data['vendor']['double']['name']);
            } else {
    			$('#link-vendor-name').val(data['vendor']['name']);
            }

			$('#modal-link-vendor').foundation('open');
		}
	}, "json");
	return false;
});
{% endif %}


{% if perms.catalog.change_vendor %}
$("body").delegate("[data-do='save-link-vendor']", "click", function(){

	$.post('/catalog/ajax/link/vendor/', {
		id: $('#link-vendor-id').val(),
		name: $('#link-vendor-name').val(),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {

		if ('success' == data.status){

			$('[data-vendor-name="' + data['vendor']['id'] + '"]').text(data['vendor']['name']);
			$('[data-vendor-state="' + data['vendor']['id'] + '"]').prop('checked', data['vendor']['state']);

			$('#modal-link-vendor').foundation('close');
		}
	}, "json");

	return false;
});
{% endif %}


{% if perms.catalog.change_vendor %}
$("body").delegate("[data-do='cancel-link-vendor']", "click", function(){

	$('#edit-vendor-id').val('0');
	$('#edit-vendor-name').val('');

	$('#modal-link-vendor').foundation('close');

	return false;
});
{% endif %}


{% if perms.catalog.delete_vendor %}
$("body").delegate("[data-do='open-delete-vendor']", "click", function(){

	model = 'vendor';

	$.post('/catalog/ajax/get/' + model + '/', {
		id : $(this).data(model + '-id'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {
		if ('success' == data.status){

			$('#delete-' + model + '-id').val(data[model]['id']);
			$('#delete-' + model + '-name').text(data[model]['name'])

			$('#modal-delete-' + model).foundation('open');
		}
	}, "json");

	return false;
});
{% endif %}


{% if perms.catalog.delete_vendor %}
$("body").delegate("[data-do='delete-vendor-apply']", "click", function(){

	model = 'vendor';

	$.post('/catalog/ajax/delete/' + model + '/', {
		id : $('#delete-' + model + '-id').val(),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {
		if ('success' == data.status) {

			$('[data-' + model + '="' + data['id'] + '"]').empty();

			$('#modal-delete-' + model).foundation('close');
		}
	}, "json");

	return false;
});
{% endif %}


{% if perms.catalog.delete_vendor %}
$("body").delegate("[data-do='delete-vendor-cancel']", "click", function(){

	model = 'vendor';

	$('#delete-' + model + '-id').val(0);

	$('#modal-delete-' + model).foundation('close');

	return false;
});
{% endif %}


{% if perms.catalog.change_vendor %}
$("body").delegate("[data-do='switch-vendor-state']", "click", function(){

	model = 'vendor';

	$.post('/catalog/ajax/switch-state/' + model + '/', {
		id    : $(this).data(model + '-id'),
		state : $(this).prop('checked'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
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
