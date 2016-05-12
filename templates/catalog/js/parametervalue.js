// Open New
{% if perms.catalog.add_parametervalue %}
$("body").delegate("[data-do='open-new-parametervalue']", "click", function(){

	model = 'parametervalue';

	$('#modal-edit-' + model + '-header').text('Добавить значение параметра');

	$('#edit-' + model + '-id').val('0');
	$('#edit-' + model + '-parameter').val('0');
	$('#edit-' + model + '-name').val('');
	$('#edit-' + model + '-order').val('0');
	$('#edit-' + model + '-state').prop('checked', true);

	$('#modal-edit-' + model).foundation('reveal', 'open');

	return false;
});
{% endif %}


// Open Edit
{% if perms.catalog.change_parametervalue %}
$("body").delegate("[data-do='open-edit-parametervalue']", "click", function(){

	model = 'parametervalue';

	$.post('/catalog/ajax/get/' + model + '/', {
		id : $(this).data(model + '-id'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {
		if ('success' == data.status){

			$('#modal-edit-' + model + '-header').text('Редактировать значение параметра');

			$('#edit-' + model + '-id').val(data[model]['id']);

			key = 'parameter';
			if (data[model][key]) {
				$('#edit-' + model + '-' + key).val(data[model][key]['id']);
			} else {
				$('#edit-' + model + '-' + key).val(0);
			}

			$('#edit-' + model + '-name').val(data[model]['name']);
			$('#edit-' + model + '-order').val(data[model]['order']);
			$('#edit-' + model + '-state').prop('checked', data[model]['state']);

			$('#modal-edit-' + model).foundation('reveal', 'open');
		}
	}, "json");

	return false;
});
{% endif %}


// Save
{% if perms.catalog.change_parametervalue %}
$("body").delegate("[data-do='edit-parametervalue-save']", "click", function(){

	model = 'parametervalue';

	$.post('/catalog/ajax/save/' + model + '/', {
		id           : $('#edit-' + model + '-id').val(),
		parameter_id : $('#edit-' + model + '-parameter').val(),
		name         : $('#edit-' + model + '-name').val(),
		order        : $('#edit-' + model + '-order').val(),
		state        : $('#edit-' + model + '-state').prop('checked'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {
		if ('success' == data.status){

			key = 'parameter';
			if (data[model][key]) {
				$('[data-' + model + '-' + key + '-name="' + data[model]['id'] + '"]').text(data[model][key]['name']);
				$('[data-' + model + '-' + key + '-name="' + data[model]['id'] + '"]').data(key + '-id', data[model][key]['id']);
				$('[data-' + model + '-' + key + '-name="' + data[model]['id'] + '"]').data(key + '-name', data[model][key]['id']);
			} else {
				$('[data-' + model + '-' + key + '-name="' + data[model]['id'] + '"]').text('');
				$('[data-' + model + '-' + key + '-name="' + data[model]['id'] + '"]').data(key + '-id', '0');
				$('[data-' + model + '-' + key + '-name="' + data[model]['id'] + '"]').data(key + '-name', '0');
			}

			$('[data-' + model + '-value="' + data[model]['id'] + '"]').text(data[model]['name']);

			$('[data-' + model + '-state="' + o.id + '"]').prop('checked', data[model]['state']);

			$('#edit-' + model + '-id').val('0');
			$('#edit-' + model + '-parameter').val('0');
			$('#edit-' + model + '-name').val('');
			$('#edit-' + model + '-order').val('0');
			$('#edit-' + model + '-state').prop('checked', false);

			$('#modal-edit-' + model).foundation('reveal', 'close');
		}
	}, "json");

	return false;
});
{% endif %}


// Cancel Edit
{% if perms.catalog.change_parametervalue %}
$("body").delegate("[data-do='edit-parametervalue-cancel']", "click", function(){

	model = 'parametervalue';

	$('#edit-' + model + '-id').val('0');
	$('#edit-' + model + '-parameter').val('0');
	$('#edit-' + model + '-name').val('');
	$('#edit-' + model + '-order').val('0');
	$('#edit-' + model + '-state').prop('checked', false);

	$('#modal-edit-' + model).foundation('reveal', 'close');

	return false;
});
{% endif %}


// Open Delete
{% if perms.catalog.delete_parametervalue %}
$("body").delegate("[data-do='open-delete-parametervalue']", "click", function(){

	model = 'parametervalue';

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
{% if perms.catalog.delete_parametervalue %}
$("body").delegate("[data-do='delete-parametervalue-apply']", "click", function(){

	model = 'parametervalue';

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
{% if perms.catalog.delete_parametervalue %}
$("body").delegate("[data-do='delete-parameter-cancel']", "click", function(){

	model = 'parametervalue';

	$('#delete-' + model + '-id').val(0);

	$('#modal-delete-' + model).foundation('reveal', 'close');

	return false;
});
{% endif %}


// Switch State
{% if perms.catalog.change_parametervalue %}
$("body").delegate("[data-do='switch-parametervalue-state']", "click", function(){

	model = 'parametervalue';

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
