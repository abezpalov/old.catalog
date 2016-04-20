// Open New
{% if perms.catalog.change_pricetype %}
$("body").delegate("[data-do='open-new-pricetype']", "click", function(){

	model = 'pricetype';

	$('#modal-edit-' + model + '-header').text('Добавить тип данных параметров');

	$('#edit-' + model + '-id').val('0');
	$('#edit-' + model + '-name').val('');
	$('#edit-' + model + '-alias').val('');
	$('#edit-' + model + '-multiplier').val('1.0');
	$('#edit-' + model + '-alias').val('');
	$('#edit-' + model + '-state').prop('checked', true);

	$('#modal-edit-' + model).foundation('reveal', 'open');

	return false;
});
{% endif %}

// Open Edit
{% if perms.catalog.change_pricetype %}
$("body").delegate("[data-do='open-edit-pricetype']", "click", function(){

	model = 'pricetype';

	$.post('/catalog/ajax/get/' + model + '/', {
		id : $(this).data(model + '-id'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {
		if ('success' == data.status){

			$('#modal-edit-' + model + '-header').text('Редактировать тип цены');

			$('#edit-' + model + '-id').val(data[model]['id']);
			$('#edit-' + model + '-name').val(data[model]['name']);
			$('#edit-' + model + '-alias').val(data[model]['alias']);
			$('#edit-' + model + '-multiplier').val(data[model]['multiplier']);
			$('#edit-' + model + '-state').prop('checked', data[model]['state']);

			$('#modal-edit-' + model).foundation('reveal', 'open');

		}
	}, "json");

	return false;
});
{% endif %}


// Save
{% if perms.catalog.change_pricetype %}
$("body").delegate("[data-do='edit-pricetype-save']", "click", function(){

	model = 'pricetype';

	$.post('/catalog/ajax/save/' + model + '/', {
		id         : $('#edit-' + model + '-id').val(),
		name       : $('#edit-' + model + '-name').val(),
		alias      : $('#edit-' + model + '-alias').val(),
		multiplier : $('#edit-' + model + '-multiplier').val(),
		state      : $('#edit-' + model + '-state').prop('checked'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {

		if ('success' == data.status){

			$('[data-' + model + '-name="' + data[model]['id'] + '"]').text(data[model]['name']);
			$('[data-' + model + '-multiplier="' + data[model]['id'] + '"]').text(data[model]['multiplier']);
			$('[data-' + model + '-state="' + data[model]['id'] + '"]').prop('checked', data[model]['state']);

			$('#edit-' + model + '-id').val('0');
			$('#edit-' + model + '-name').val('');
			$('#edit-' + model + '-alias').val('');
			$('#edit-' + model + '-multiplier').val('1.0');
			$('#edit-' + model + '-state').prop('checked', false);

			$('#modal-edit-' + model).foundation('reveal', 'close');
		}
	}, "json");

	return false;
});
{% endif %}


// Cancel Edit
{% if perms.catalog.change_pricetype %}
$("body").delegate("[data-do='edit-pricetype-cancel']", "click", function(){

	model = 'pricetype';

	$('#edit-' + model + '-id').val('0');
	$('#edit-' + model + '-name').val('');
	$('#edit-' + model + '-alias').val('');
	$('#edit-' + model + '-multiplier').val('1.0');
	$('#edit-' + model + '-state').prop('checked', false);

	$('#modal-edit-' + model).foundation('reveal', 'close');

	return false;
});
{% endif %}


// Open Delete
{% if perms.catalog.delete_pricetype %}
$("body").delegate("[data-do='open-delete-pricetype']", "click", function(){

	model = 'pricetype';

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
{% if perms.catalog.delete_pricetype %}
$("body").delegate("[data-do='delete-pricetype-apply']", "click", function(){

	model = 'pricetype';

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
{% if perms.catalog.delete_pricetype %}
$("body").delegate("[data-do='delete-pricetype-cancel']", "click", function(){

	model = 'pricetype';

	$('#delete-' + model + '-id').val(0);

	$('#modal-delete-' + model).foundation('reveal', 'close');

	return false;
});
{% endif %}


// Switch State
{% if perms.catalog.change_pricetype %}
$("body").delegate("[data-do='switch-pricetype-state']", "click", function(){

	model = 'pricetype';

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
