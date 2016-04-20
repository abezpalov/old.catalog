// Open New
{% if perms.catalog.add_unit %}
$("body").delegate("[data-do='open-new-unit']", "click", function(){

	model_name = 'unit';

	$('#modal-edit-' + model_name + '-header').text('Добавить единицу измерения');

	$('#edit-' + model_name + '-id').val('0');
	$('#edit-' + model_name + '-name').val('');
	$('#edit-' + model_name + '-name-short').val('');
	$('#edit-' + model_name + '-name-short-xml').val('');
	$('#edit-' + model_name + '-alias').val('');
	$('#edit-' + model_name + '-state').prop('checked', true);

	$('#modal-edit-' + model_name).foundation('reveal', 'open');

	return false;
});
{% endif %}


// Open Edit
{% if perms.catalog.change_unit %}
$("body").delegate("[data-do='open-edit-unit']", "click", function(){

	model_name = 'unit';

	$.post('/catalog/ajax/get/' + model_name + '/', {
		id : $(this).data(model_name + '-id'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {
		if ('success' == data.status){

			$('#modal-edit-' + model_name + '-header').text('Редактировать единицу измерения');

			$('#edit-' + model_name + '-id').val(data[model_name]['id']);
			$('#edit-' + model_name + '-name').val(data[model_name]['name']);
			$('#edit-' + model_name + '-name-short').val(data[model_name]['name_short']);
			$('#edit-' + model_name + '-name-short-xml').val(data[model_name]['name_short_xml']);
			$('#edit-' + model_name + '-alias').val(data[model_name]['alias']);
			$('#edit-' + model_name + '-state').prop('checked', data[model_name]['state']);

			$('#modal-edit-' + model_name).foundation('reveal', 'open');
		}
	}, "json");

	return false;
});
{% endif %}


// Save
{% if perms.catalog.change_unit %}
$("body").delegate("[data-do='edit-unit-save']", "click", function(){

	model_name = 'unit';

	$.post('/catalog/ajax/save/' + model_name + '/', {
		id             : $('#edit-' + model_name + '-id').val(),
		name           : $('#edit-' + model_name + '-name').val(),
		name_short     : $('#edit-' + model_name + '-name-short').val(),
		name_short_xml : $('#edit-' + model_name + '-name-short-xml').val(),
		alias          : $('#edit-' + model_name + '-alias').val(),
		state          : $('#edit-' + model_name + '-state').prop('checked'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {

		if ('success' == data.status){


			$('[data-' + model_name + '-name="' + data[model_name]['id'] + '"]').text(data[model_name]['name']);
			$('[data-' + model_name + '-state="' + data[model_name]['id'] + '"]').prop('checked', data[model_name]['state']);

			$('#edit-' + model_name + '-id').val('0');
			$('#edit-' + model_name + '-name').val('');
			$('#edit-' + model_name + '-name-short').val('');
			$('#edit-' + model_name + '-name-short-xml').val('');
			$('#edit-' + model_name + '-alias').val('');
			$('#edit-' + model_name + '-state').prop('checked', false);

			$('#modal-edit-' + model_name).foundation('reveal', 'close');
		}
	}, "json");

	return false;
});
{% endif %}


// Cancel Edit
{% if perms.catalog.change_unit %}
$("body").delegate("[data-do='edit-unit-cancel']", "click", function(){

	model_name = 'unit';

	$('#edit-' + model_name + '-id').val('0');
	$('#edit-' + model_name + '-name').val('');
	$('#edit-' + model_name + '-name-short').val('');
	$('#edit-' + model_name + '-name-short-xml').val('');
	$('#edit-' + model_name + '-alias').val('');
	$('#edit-' + model_name + '-state').prop('checked', false);

	$('#modal-edit-' + model_name).foundation('reveal', 'close');

	return false;
});
{% endif %}


// Open Delete
{% if perms.catalog.delete_unit %}
$("body").delegate("[data-do='open-delete-unit']", "click", function(){

	model_name = 'unit';

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
{% if perms.catalog.delete_unit %}
$("body").delegate("[data-do='delete-unit-apply']", "click", function(){

	model_name = 'unit';

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
{% if perms.catalog.delete_unit %}
$("body").delegate("[data-do='delete-unit-cancel']", "click", function(){

	model_name = 'unit';

	$('#delete-' + model_name + '-id').val(0);

	$('#modal-delete-' + model_name).foundation('reveal', 'close');

	return false;
});
{% endif %}


// Switch State
{% if perms.catalog.change_unit %}
$("body").delegate("[data-do='switch-unit-state']", "click", function(){

	model_name = 'unit';

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
