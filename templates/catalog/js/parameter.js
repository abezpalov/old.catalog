// Open New
{% if perms.catalog.add_parameter %}
$("body").delegate("[data-do='open-new-parameter']", "click", function(){

	model = 'parameter';

	$('#modal-edit-' + model + '-header').text('Добавить параметр');

	$('#edit-' + model + '-id').val('0');
	$('#edit-' + model + '-name').val('');
	$('#edit-' + model + '-alias').val('');
	$('#edit-' + model + '-parametertype').val('0');
	$('#edit-' + model + '-order').val('0');
	$('#edit-' + model + '-state').prop('checked', true);

	$('#modal-edit-' + model).foundation('reveal', 'open');

	return false;
});
{% endif %}


// Open Edit
{% if perms.catalog.change_parameter %}
$("body").delegate("[data-do='open-edit-parameter']", "click", function(){

	model = 'parameter';

	$.post('/catalog/ajax/get/' + model + '/', {
		id : $(this).data(model + '-id'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {
		if ('success' == data.status){

			$('#modal-edit-' + model + '-header').text('Редактировать параметр');

			$('#edit-' + model + '-id').val(data[model]['id']);
			$('#edit-' + model + '-name').val(data[model]['name']);
			$('#edit-' + model + '-alias').val(data[model]['alias']);
			if (data[model]['parametertype']) {
				$('#edit-' + model + '-parametertype').val(data[model]['parametertype']['id']);
			} else {
				$('#edit-' + model + '-parametertype').val(0);
			}
			$('#edit-' + model + '-order').val(data[model]['order']);
			$('#edit-' + model + '-state').prop('checked', data[model]['state']);

			$('#modal-edit-' + model).foundation('reveal', 'open');
		}
	}, "json");

	return false;
});
{% endif %}


// Save
{% if perms.catalog.change_parameter %}
$("body").delegate("[data-do='edit-parameter-save']", "click", function(){

	model = 'parameter';

	$.post('/catalog/ajax/save/' + model + '/', {
		id               : $('#edit-' + model + '-id').val(),
		name             : $('#edit-' + model + '-name').val(),
		alias            : $('#edit-' + model + '-alias').val(),
		parametertype_id : $('#edit-' + model + '-parametertype').val(),
		order            : $('#edit-' + model + '-order').val(),
		state            : $('#edit-' + model + '-state').prop('checked'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {

		if ('success' == data.status){


			$('[data-' + model + '-name="' + data[model]['id'] + '"]').text(data[model]['name']);
			$('[data-' + model + '-state="' + data[model]['id'] + '"]').prop('checked', data[model]['state']);

			if (data[model]['parametertype']) {
				$('[data-' + model + '-parametertype-name="' + data[model]['id'] + '"]').text(data[model]['parametertype']['name']);
				$('[data-' + model + '-parametertype-name="' + data[model]['id'] + '"]').data('parametertype-id', data[model]['parametertype']['id']);
				$('[data-' + model + '-parametertype-name="' + data[model]['id'] + '"]').data('parametertype-name', data[model]['parametertype']['id']);
			} else {
				$('[data-' + model + '-parametertype-name="' + data[model]['id'] + '"]').text('');
				$('[data-' + model + '-parametertype-name="' + data[model]['id'] + '"]').data('parametertype-id', '0');
				$('[data-' + model + '-parametertype-name="' + data[model]['id'] + '"]').data('parametertype-name', '0');
			}

			$('#edit-' + model + '-id').val('0');
			$('#edit-' + model + '-name').val('');
			$('#edit-' + model + '-alias').val('');
			$('#edit-' + model + '-parametertype').val('');
			$('#edit-' + model + '-order').val('0');
			$('#edit-' + model + '-state').prop('checked', false);

			$('#modal-edit-' + model).foundation('reveal', 'close');
		}
	}, "json");

	return false;
});
{% endif %}


// Cancel Edit
{% if perms.catalog.change_parameter %}
$("body").delegate("[data-do='edit-parameter-cancel']", "click", function(){

	model = 'parameter';

	$('#edit-' + model + '-id').val('0');
	$('#edit-' + model + '-name').val('');
	$('#edit-' + model + '-alias').val('');
	$('#edit-' + model + '-parametertype').val('');
	$('#edit-' + model + '-order').val('0');
	$('#edit-' + model + '-state').prop('checked', false);

	$('#modal-edit-' + model).foundation('reveal', 'close');

	return false;
});
{% endif %}


// Open Delete
{% if perms.catalog.delete_parameter %}
$("body").delegate("[data-do='open-delete-parameter']", "click", function(){

	model = 'parameter';

	$.post('/catalog/ajax/get/' + model + '/', {
		id : $(this).data(model + '-id'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {
		if ('success' == data.status){

			$('#delete-' + model + '-id').val(data[model]['id']);
			$('#delete-' + model + '-name').text(data[model]['name'])

			$('#modal-delete-' + model).foundation('reveal', 'open');
		}
	}, "json");

	return false;
});
{% endif %}


// Delete
{% if perms.catalog.delete_parameter %}
$("body").delegate("[data-do='delete-parameter-apply']", "click", function(){

	model = 'parameter';

	$.post('/catalog/ajax/delete/' + model + '/', {
		id : $('#delete-' + model + '-id').val(),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {
		if ('success' == data.status) {

			$('[data-' + model + '="' + data['id'] + '"]').empty();

			$('#modal-delete-' + model).foundation('reveal', 'close');
		}
	}, "json");

	return false;
});
{% endif %}


// Cancel Delete
{% if perms.catalog.delete_parameter %}
$("body").delegate("[data-do='delete-parameter-cancel']", "click", function(){

	model = 'parameter';

	$('#delete-' + model + '-id').val(0);

	$('#modal-delete-' + model).foundation('reveal', 'close');

	return false;
});
{% endif %}


// Switch State
{% if perms.catalog.change_parameter %}
$("body").delegate("[data-do='switch-parameter-state']", "click", function(){

	model = 'parameter';

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
