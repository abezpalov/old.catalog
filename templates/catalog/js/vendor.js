{% if perms.catalog.add_vendor %}
$("body").delegate("[data-do='open-new-vendor']", "click", function(){

	model = 'vendor';

	$('#modal-edit-' + model + '-header').text('Добавить производителя');

	$('#edit-' + model + '-id').val('0');
	$('#edit-' + model + '-name').val('');
	$('#edit-' + model + '-alias').val('');
	$('#edit-' + model + '-description').val('');
	$('#edit-' + model + '-state').prop('checked', true);

	$('#modal-edit-' + model).foundation('open');

	return false;
});
{% endif %}


{% if perms.catalog.change_vendor %}
$("body").delegate("[data-do='open-edit-vendor']", "click", function(){

	model = 'vendor';

	$.post('/catalog/ajax/get/' + model + '/', {
		id : $(this).data(model + '-id'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {
		if ('success' == data.status){

			$('#modal-edit-' + model + '-header').text('Редактировать производителя');

			$('#edit-' + model + '-id').val(data[model]['id']);
			$('#edit-' + model + '-name').val(data[model]['name']);
			$('#edit-' + model + '-alias').val(data[model]['alias']);
			$('#edit-' + model + '-description').val(data[model]['description']);
			$('#edit-' + model + '-state').prop('checked', data[model]['state']);

			$('#modal-edit-' + model).foundation('open');
		}
	}, "json");

	return false;
});
{% endif %}


{% if perms.catalog.change_stock %}
$("body").delegate("[data-do='edit-vendor-save']", "click", function(){

	model = 'vendor';


	$.post('/catalog/ajax/save/' + model + '/', {
		id          : $('#edit-' + model + '-id').val(),
		name        : $('#edit-' + model + '-name').val(),
		alias       : $('#edit-' + model + '-alias').val(),
		description : $('#edit-' + model + '-description').val(),
		state       : $('#edit-' + model + '-state').prop('checked'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {

		if ('success' == data.status){

			$('[data-' + model + '-name="' + data[model]['id'] + '"]').text(data[model]['name']);
			$('[data-' + model + '-state="' + data[model]['id'] + '"]').prop('checked', data[model]['state']);

			$('#edit-' + model + '-id').val('0');
			$('#edit-' + model + '-name').val('');
			$('#edit-' + model + '-alias').val('');
			$('#edit-' + model + '-description').val('');
			$('#edit-' + model + '-state').prop('checked', false);

			$('#modal-edit-' + model).foundation('close');
		}
	}, "json");

	return false;
});
{% endif %}


{% if perms.catalog.change_vendor %}
$("body").delegate("[data-do='edit-vendor-cancel']", "click", function(){

	model = 'vendor';

	$('#edit-' + model + '-id').val('0');
	$('#edit-' + model + '-name').val('');
	$('#edit-' + model + '-alias').val('');
	$('#edit-' + model + '-description').val('');
	$('#edit-' + model + '-state').prop('checked', false);

	$('#modal-edit-' + model).foundation('close');

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
