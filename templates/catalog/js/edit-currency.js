// Open New
{% if perms.catalog.add_currency %}
$("body").delegate("[data-do='open-new-currency']", "click", function(){

	model_name = 'currency';

	$('#modal-edit-' + model_name +'-header').text('Добавить валюту');

	$('#edit-' + model_name +'-id').val('0');
	$('#edit-' + model_name +'-name').val('');
	$('#edit-' + model_name +'-fulle-name').val('');
	$('#edit-' + model_name +'-alias').val('');
	$('#edit-' + model_name +'-rate').val('0.0');
	$('#edit-' + model_name +'-quantity').val('0');
	$('#edit-' + model_name +'-state').prop('checked', false);

	$('#modal-edit-' + model_name).foundation('reveal', 'open');

	return false;
});
{% endif %}


// Open Edit
{% if perms.catalog.change_currency %}
$("body").delegate("[data-do='open-edit-currency']", "click", function(){

	model_name = 'currency';

	$.post('/catalog/ajax/get/' + model_name + '/', {
		id : $(this).data(model_name + '-id'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {
		if ('success' == data.status){

			$('#modal-edit-' + model_name +'-header').text('Редактировать валюту');

			$('#edit-' + model_name +'-id').val(data.currency['id']);
			$('#edit-' + model_name +'-name').val(data.currency['name']);
			$('#edit-' + model_name +'-full-name').val(data.currency['full_name']);
			$('#edit-' + model_name +'-alias').val(data.currency['alias']);
			$('#edit-' + model_name +'-rate').val(data.currency['rate']);
			$('#edit-' + model_name +'-quantity').val(data.currency['quantity']);
			$('#edit-' + model_name +'-state').prop('checked', data.currency['state']);

			$('#modal-edit-' + model_name).foundation('reveal', 'open');
		}
	}, "json");

	return false;
});
{% endif %}


// Save
{% if perms.catalog.change_currency %}
$("body").delegate("[data-do='edit-currency-save']", "click", function(){

	model_name = 'currency';

	$.post('/catalog/ajax/save/' + model_name +'/', {
		id        : $('#edit-' + model_name +'-id').val(),
		name      : $('#edit-' + model_name +'-name').val(),
		full_name : $('#edit-' + model_name +'-full-name').val(),
		alias     : $('#edit-' + model_name +'-alias').val(),
		rate      : $('#edit-' + model_name +'-rate').val(),
		quantity  : $('#edit-' + model_name +'-quantity').val(),
		state     : $('#edit-' + model_name +'-state').prop('checked'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {

		if ('success' == data.status){

			$('[data-' + model_name +'-full-name="' + data[model_name]['id'] + '"]').text(data[model_name]['full_name']);
			$('[data-' + model_name +'-alias="' + data[model_name]['id'] + '"]').text(data[model_name]['alias']);
			$('[data-' + model_name +'-state="' + data[model_name]['id'] + '"]').prop('checked', data[model_name]['state']);
			$('[data-' + model_name +'-rate="' + data[model_name]['id'] + '"]').text(data[model_name]['rate']);
			$('[data-' + model_name +'-quantity="' + data[model_name]['id'] + '"]').text(data[model_name]['quantity']);

			$('#edit-' + model_name +'-id').val('0');
			$('#edit-' + model_name +'-name').val('');
			$('#edit-' + model_name +'-fulle-name').val('');
			$('#edit-' + model_name +'-alias').val('');
			$('#edit-' + model_name +'-rate').val('0.0');
			$('#edit-' + model_name +'-quantity').val('0.0');
			$('#edit-' + model_name +'-state').prop('checked', false);

			$('#modal-edit-' + model_name).foundation('reveal', 'close');
		}
	}, "json");

	return false;
});
{% endif %}


// Cancel Edit
{% if perms.catalog.change_category %}
$("body").delegate("[data-do='edit-currency-cancel']", "click", function(){

	model_name = 'currency';

	$('#edit-' + model_name + '-id').val('0');
	$('#edit-' + model_name + '-name').val('');
	$('#edit-' + model_name + '-fulle-name').val('');
	$('#edit-' + model_name + '-alias').val('');
	$('#edit-' + model_name + '-rate').val('0.0');
	$('#edit-' + model_name + '-quantity').val('0');
	$('#edit-' + model_name + '-state').prop('checked', false);

	$('#modal-edit-' + model_name).foundation('reveal', 'close');

	return false;
});
{% endif %}


// Open Delete
{% if perms.catalog.delete_currency %}
$("body").delegate("[data-do='open-delete-currency']", "click", function(){

	model_name = 'currency';

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
{% if perms.catalog.delete_currency %}
$("body").delegate("[data-do='delete-currency-apply']", "click", function(){

	model_name = 'currency';

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
{% if perms.catalog.delete_currency %}
$("body").delegate("[data-do='delete-currency-cancel']", "click", function(){

	model_name = 'currency';

	$('#delete-' + model_name + '-id').val(0);

	$('#modal-delete-' + model_name).foundation('reveal', 'close');

	return false;
});
{% endif %}


// Switch State
{% if perms.catalog.change_currency %}
$("body").delegate("[data-do='switch-currency-state']", "click", function(){

	model_name = 'currency';

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
