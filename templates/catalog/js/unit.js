// Open New
{% if perms.catalog.add_unit %}
$("body").delegate("[data-do='open-new-unit']", "click", function(){

	model = 'unit';

	$('#modal-edit-' + model + '-header').text('Добавить единицу измерения');

	$('#edit-' + model + '-id').val('0');
	$('#edit-' + model + '-name').val('');
	$('#edit-' + model + '-name-short').val('');
	$('#edit-' + model + '-name-short-xml').val('');
	$('#edit-' + model + '-alias').val('');
	$('#edit-' + model + '-state').prop('checked', true);

	$('#modal-edit-' + model).foundation('reveal', 'open');

	return false;
});
{% endif %}


// Open Edit
{% if perms.catalog.change_unit %}
$("body").delegate("[data-do='open-edit-unit']", "click", function(){

	model = 'unit';

	$.post('/catalog/ajax/get/' + model + '/', {
		id : $(this).data(model + '-id'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {
		if ('success' == data.status){

			$('#modal-edit-' + model + '-header').text('Редактировать единицу измерения');

			$('#edit-' + model + '-id').val(data[model]['id']);
			$('#edit-' + model + '-name').val(data[model]['name']);
			$('#edit-' + model + '-name-short').val(data[model]['name_short']);
			$('#edit-' + model + '-name-short-xml').val(data[model]['name_short_xml']);
			$('#edit-' + model + '-alias').val(data[model]['alias']);
			$('#edit-' + model + '-state').prop('checked', data[model]['state']);

			$('#modal-edit-' + model).foundation('reveal', 'open');
		}
	}, "json");

	return false;
});
{% endif %}


// Save
{% if perms.catalog.change_unit %}
$("body").delegate("[data-do='edit-unit-save']", "click", function(){

	model = 'unit';

	$.post('/catalog/ajax/save/' + model + '/', {
		id             : $('#edit-' + model + '-id').val(),
		name           : $('#edit-' + model + '-name').val(),
		name_short     : $('#edit-' + model + '-name-short').val(),
		name_short_xml : $('#edit-' + model + '-name-short-xml').val(),
		alias          : $('#edit-' + model + '-alias').val(),
		state          : $('#edit-' + model + '-state').prop('checked'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {

		if ('success' == data.status){


			$('[data-' + model + '-name="' + data[model]['id'] + '"]').text(data[model]['name']);
			$('[data-' + model + '-state="' + data[model]['id'] + '"]').prop('checked', data[model]['state']);

			$('#edit-' + model + '-id').val('0');
			$('#edit-' + model + '-name').val('');
			$('#edit-' + model + '-name-short').val('');
			$('#edit-' + model + '-name-short-xml').val('');
			$('#edit-' + model + '-alias').val('');
			$('#edit-' + model + '-state').prop('checked', false);

			$('#modal-edit-' + model).foundation('reveal', 'close');
		}
	}, "json");

	return false;
});
{% endif %}


// Cancel Edit
{% if perms.catalog.change_unit %}
$("body").delegate("[data-do='edit-unit-cancel']", "click", function(){

	model = 'unit';

	$('#edit-' + model + '-id').val('0');
	$('#edit-' + model + '-name').val('');
	$('#edit-' + model + '-name-short').val('');
	$('#edit-' + model + '-name-short-xml').val('');
	$('#edit-' + model + '-alias').val('');
	$('#edit-' + model + '-state').prop('checked', false);

	$('#modal-edit-' + model).foundation('reveal', 'close');

	return false;
});
{% endif %}


// Open Delete
{% if perms.catalog.delete_unit %}
$("body").delegate("[data-do='open-delete-unit']", "click", function(){

	model = 'unit';

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
{% if perms.catalog.delete_unit %}
$("body").delegate("[data-do='delete-unit-apply']", "click", function(){

	model = 'unit';

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
{% if perms.catalog.delete_unit %}
$("body").delegate("[data-do='delete-unit-cancel']", "click", function(){

	model = 'unit';

	$('#delete-' + model + '-id').val(0);

	$('#modal-delete-' + model).foundation('reveal', 'close');

	return false;
});
{% endif %}


// Switch State
{% if perms.catalog.change_unit %}
$("body").delegate("[data-do='switch-unit-state']", "click", function(){

	model = 'unit';

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
