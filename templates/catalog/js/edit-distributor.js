// Open New
{% if perms.catalog.add_distributor %}
$("body").delegate("[data-do='open-new-distributor']", "click", function(){

	model_name = 'distributor';

	$('#modal-edit-' + model_name + '-header').text('Добавить поставика');

	$('#edit-' + model_name + '-id').val('0');
	$('#edit-' + model_name + '-name').val('');
	$('#edit-' + model_name + '-alias').val('');
	$('#edit-' + model_name + '-description').val('');
	$('#edit-' + model_name + '-state').prop('checked', true);

	$('#modal-edit-' + model_name).foundation('reveal', 'open');

	return false;
});
{% endif %}


// Open Edit
{% if perms.catalog.change_distributor %}
$("body").delegate("[data-do='open-edit-distributor']", "click", function(){

	model_name = 'distributor';

	$.post('/catalog/ajax/get/' + model_name + '/', {
		id : $(this).data(model_name + '-id'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {
		if ('success' == data.status){

			$('#modal-edit-' + model_name + '-header').text('Редактировать поставщика');

			$('#edit-' + model_name + '-id').val(data[model_name]['id']);
			$('#edit-' + model_name + '-name').val(data[model_name]['name']);
			$('#edit-' + model_name + '-alias').val(data[model_name]['alias']);
			$('#edit-' + model_name + '-description').val(data[model_name]['description']);
			$('#edit-' + model_name + '-state').prop('checked', data[model_name]['state']);

			$('#modal-edit-' + model_name).foundation('reveal', 'open');
		}
	}, "json");

	return false;
});
{% endif %}


// Save
{% if perms.catalog.change_distributor %}
$("body").delegate("[data-do='edit-distributor-save']", "click", function(){

	model_name = 'distributor';

	$.post('/catalog/ajax/save/' + model_name + '/', {
		id          : $('#edit-' + model_name + '-id').val(),
		name        : $('#edit-' + model_name + '-name').val(),
		alias       : $('#edit-' + model_name + '-alias').val(),
		description : $('#edit-' + model_name + '-description').val(),
		state       : $('#edit-' + model_name + '-state').prop('checked'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {

		if ('success' == data.status){

			$("[data-" + model_name + "-name='" + $('#edit-' + model_name + '-id').val() + "']").text(data[model_name]['name']);
			$("[data-" + model_name + "-state='" + $('#edit-' + model_name + '-id').val() + "']").prop('checked', data[model_name]['state']);

			$('#edit-' + model_name + '-id').val('0');
			$('#edit-' + model_name + '-name').val('');
			$('#edit-' + model_name + '-alias').val('');
			$('#edit-' + model_name + '-description').val('');
			$('#edit-' + model_name + '-state').prop('checked', false);

			$('#modal-edit-' + model_name).foundation('reveal', 'close');
		}
	}, "json");

	return false;
});
{% endif %}


// Cancel Edit
{% if perms.catalog.change_distributor %}
$("body").delegate("[data-do='edit-distributor-cancel']", "click", function(){

	model_name = 'distributor';

	$('#edit-' + model_name + '-id').val('0');
	$('#edit-' + model_name + '-name').val('');
	$('#edit-' + model_name + '-alias').val('');
	$('#edit-' + model_name + '-description').val('');
	$('#edit-' + model_name + '-state').prop('checked', false);

	$('#modal-edit-' + model_name).foundation('reveal', 'close');

	return false;
});
{% endif %}


// Open Delete
{% if perms.catalog.delete_distributor %}
$("body").delegate("[data-do='open-delete-distributor']", "click", function(){

	model_name = 'distributor';

	$.post('/catalog/ajax/get/' + model_name + '/', {
		id : $(this).data(model_name + '-id'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {
		if ('success' == data.status){

			$('#delete-' + model_name + '-id').val(data[model_name]['id']);
			$('#delete-' + model_name + '-name').text(data[model_name]['name'])

			$('#modal-delete-' + model_name).foundation('reveal', 'open');
		}
	}, "json");

	return false;
});
{% endif %}


// Delete
{% if perms.catalog.delete_distributor %}
$("body").delegate("[data-do='delete-distributor-apply']", "click", function(){

	model_name = 'distributor';

	$.post('/catalog/ajax/delete/' + model_name + '/', {
		id : $('#delete-' + model_name + '-id').val(),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {
		if ('success' == data.status) {

			$('[data-' + model_name + '="' + data['id'] + '"]').empty();

			$('#modal-delete-' + model_name).foundation('reveal', 'close');
		}
	}, "json");

	return false;
});
{% endif %}


// Cancel Delete
{% if perms.catalog.delete_distributor %}
$("body").delegate("[data-do='delete-distributor-cancel']", "click", function(){

	model_name = 'distributor';

	$('#delete-' + model_name + '-id').val(0);

	$('#modal-delete-' + model_name).foundation('reveal', 'close');

	return false;
});
{% endif %}


// Switch State
{% if perms.catalog.change_distributor %}
$("body").delegate("[data-do='switch-distributor-state']", "click", function(){

	model_name = 'distributor';

	$.post('/catalog/ajax/switch-state/' + model_name + '/', {
		id    : $(this).data(model_name + '-id'),
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
