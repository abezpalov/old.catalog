// Open New
{% if perms.catalog.add_parametervalue %}
$("body").delegate("[data-do='open-new-parametervalue']", "click", function(){

	model_name = 'parametervalue';

	$('#modal-edit-' + model_name + '-header').text('Добавить значение параметра');

	$('#edit-' + model_name + '-id').val('0');
	$('#edit-' + model_name + '-parameter').val('0');
	$('#edit-' + model_name + '-value-text').val('');
	$('#edit-' + model_name + '-value').val('0');
	$('#edit-' + model_name + '-order').val('0');
	$('#edit-' + model_name + '-state').prop('checked', true);

	$('#modal-edit-' + model_name).foundation('reveal', 'open');

	return false;
});
{% endif %}


// Open Edit
{% if perms.catalog.change_parametervalue %}
$("body").delegate("[data-do='open-edit-parametervalue']", "click", function(){

	model_name = 'parametervalue';

	$.post('/catalog/ajax/get/' + model_name + '/', {
		id : $(this).data(model_name + '-id'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {
		if ('success' == data.status){

			$('#modal-edit-' + model_name + '-header').text('Редактировать значение параметра');

			$('#edit-' + model_name + '-id').val(data[model_name]['id']);

			key = 'parameter';
			if (data[model_name][key]) {
				$('#edit-' + model_name + '-' + key).val(data[model_name][key]['id']);
			} else {
				$('#edit-' + model_name + '-' + key).val(0);
			}

			$('#edit-' + model_name + '-value-text').val(data[model_name]['value_text']);

			key = 'unit';
			if (data[model_name][key]) {
				$('#edit-' + model_name + '-' + key).val(data[model_name][key]['id']);
			} else {
				$('#edit-' + model_name + '-' + key).val(0);
			}

			$('#edit-' + model_name + '-order').val(data[model_name]['order']);
			$('#edit-' + model_name + '-state').prop('checked', data[model_name]['state']);

			$('#modal-edit-' + model_name).foundation('reveal', 'open');
		}
	}, "json");

	return false;
});
{% endif %}


// Save
{% if perms.catalog.change_parametervalue %}
$("body").delegate("[data-do='edit-parameter-value-save']", "click", function(){

	model_name = 'parametervalue';

	$.post('/catalog/ajax/save/' + model_name + '/', {
		id           : $('#edit-' + model_name + '-id').val(),
		parameter_id : $('#edit-' + model_name + '-parameter').val(),
		value_text   : $('#edit-' + model_name + '-value-text').val(),
		order        : $('#edit-' + model_name + '-order').val(),
		state        : $('#edit-' + model_name + '-state').prop('checked'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {
		if ('success' == data.status){

			key = 'parameter';
			if (data[model_name][key]) {
				$('[data-' + model_name + '-' + key + '-name="' + data[model_name]['id'] + '"]').text(data[model_name][key]['name']);
				$('[data-' + model_name + '-' + key + '-name="' + data[model_name]['id'] + '"]').data(key + '-id', data[model_name][key]['id']);
				$('[data-' + model_name + '-' + key + '-name="' + data[model_name]['id'] + '"]').data(key + '-name', data[model_name][key]['id']);
			} else {
				$('[data-' + model_name + '-' + key + '-name="' + data[model_name]['id'] + '"]').text('');
				$('[data-' + model_name + '-' + key + '-name="' + data[model_name]['id'] + '"]').data(key + '-id', '0');
				$('[data-' + model_name + '-' + key + '-name="' + data[model_name]['id'] + '"]').data(key + '-name', '0');
			}

			$('[data-' + model_name + '-value="' + data[model_name]['id'] + '"]').text(data[model_name]['value_search']);

			key = 'unit';
			if (data[model_name][key]) {
				$('[data-' + model_name + '-' + key + '-name="' + data[model_name]['id'] + '"]').text(data[model_name][key]['name']);
				$('[data-' + model_name + '-' + key + '-name="' + data[model_name]['id'] + '"]').data(key + '-id', data[model_name][key]['id']);
				$('[data-' + model_name + '-' + key + '-name="' + data[model_name]['id'] + '"]').data(key + '-name', data[model_name][key]['id']);
			} else {
				$('[data-' + model_name + '-' + key + '-name="' + data[model_name]['id'] + '"]').text('');
				$('[data-' + model_name + '-' + key + '-name="' + data[model_name]['id'] + '"]').data(key + '-id', '0');
				$('[data-' + model_name + '-' + key + '-name="' + data[model_name]['id'] + '"]').data(key + '-name', '0');
			}

			$('[data-' + model_name + '-state="' + o.id + '"]').prop('checked', data[model_name]['state']);

			$('#edit-' + model_name + '-id').val('0');
			$('#edit-' + model_name + '-parameter').val('0');
			$('#edit-' + model_name + '-value-text').val('');
			$('#edit-' + model_name + '-order').val('0');
			$('#edit-' + model_name + '-state').prop('checked', false);

			$('#modal-edit-' + model_name).foundation('reveal', 'close');
		}
	}, "json");

	return false;
});
{% endif %}


// Cancel Edit
{% if perms.catalog.change_parametervalue %}
$("body").delegate("[data-do='edit-parameter-value-cancel']", "click", function(){

	model_name = 'parametervalue';

	$('#edit-' + model_name + '-id').val('0');
	$('#edit-' + model_name + '-parameter').val('0');
	$('#edit-' + model_name + '-value-text').val('');
	$('#edit-' + model_name + '-order').val('0');
	$('#edit-' + model_name + '-state').prop('checked', false);

	$('#modal-edit-' + model_name).foundation('reveal', 'close');

	return false;
});
{% endif %}


// Open Delete
{% if perms.catalog.delete_parametervalue %}
$("body").delegate("[data-do='open-delete-parametervalue']", "click", function(){

	model_name = 'parametervalue';

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
{% if perms.catalog.delete_parametervalue %}
$("body").delegate("[data-do='delete-parametervalue-apply']", "click", function(){

	model_name = 'parametervalue';

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
{% if perms.catalog.delete_parametervalue %}
$("body").delegate("[data-do='delete-parameter-cancel']", "click", function(){

	model_name = 'parametervalue';

	$('#delete-' + model_name + '-id').val(0);

	$('#modal-delete-' + model_name).foundation('reveal', 'close');

	return false;
});
{% endif %}


// Switch State
{% if perms.catalog.change_parametervalue %}
$("body").delegate("[data-do='switch-parametervalue-state']", "click", function(){

	model_name = 'parametervalue';

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
