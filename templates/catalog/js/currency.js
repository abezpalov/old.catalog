// Open New
{% if perms.catalog.add_currency %}
$("body").delegate("[data-do='open-new-currency']", "click", function(){

	model = 'currency';

	$('#modal-edit-' + model +'-header').text('Добавить валюту');

	$('#edit-' + model +'-id').val('0');
	$('#edit-' + model +'-name').val('');
	$('#edit-' + model +'-fulle-name').val('');
	$('#edit-' + model +'-alias').val('');
	$('#edit-' + model +'-rate').val('0.0');
	$('#edit-' + model +'-quantity').val('0');
	$('#edit-' + model +'-state').prop('checked', false);

	$('#modal-edit-' + model).foundation('reveal', 'open');

	return false;
});
{% endif %}


// Open Edit
{% if perms.catalog.change_currency %}
$("body").delegate("[data-do='open-edit-currency']", "click", function(){

	model = 'currency';

	$.post('/catalog/ajax/get/' + model + '/', {
		id : $(this).data(model + '-id'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {
		if ('success' == data.status){

			$('#modal-edit-' + model +'-header').text('Редактировать валюту');

			$('#edit-' + model +'-id').val(data.currency['id']);
			$('#edit-' + model +'-name').val(data.currency['name']);
			$('#edit-' + model +'-full-name').val(data.currency['full_name']);
			$('#edit-' + model +'-alias').val(data.currency['alias']);
			$('#edit-' + model +'-rate').val(data.currency['rate']);
			$('#edit-' + model +'-quantity').val(data.currency['quantity']);
			$('#edit-' + model +'-state').prop('checked', data.currency['state']);

			$('#modal-edit-' + model).foundation('reveal', 'open');
		}
	}, "json");

	return false;
});
{% endif %}


// Save
{% if perms.catalog.change_currency %}
$("body").delegate("[data-do='edit-currency-save']", "click", function(){

	model = 'currency';

	$.post('/catalog/ajax/save/' + model +'/', {
		id        : $('#edit-' + model +'-id').val(),
		name      : $('#edit-' + model +'-name').val(),
		full_name : $('#edit-' + model +'-full-name').val(),
		alias     : $('#edit-' + model +'-alias').val(),
		rate      : $('#edit-' + model +'-rate').val(),
		quantity  : $('#edit-' + model +'-quantity').val(),
		state     : $('#edit-' + model +'-state').prop('checked'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {

		if ('success' == data.status){

			$('[data-' + model +'-full-name="' + data[model]['id'] + '"]').text(data[model]['full_name']);
			$('[data-' + model +'-alias="' + data[model]['id'] + '"]').text(data[model]['alias']);
			$('[data-' + model +'-state="' + data[model]['id'] + '"]').prop('checked', data[model]['state']);
			$('[data-' + model +'-rate="' + data[model]['id'] + '"]').text(data[model]['rate']);
			$('[data-' + model +'-quantity="' + data[model]['id'] + '"]').text(data[model]['quantity']);

			$('#edit-' + model +'-id').val('0');
			$('#edit-' + model +'-name').val('');
			$('#edit-' + model +'-fulle-name').val('');
			$('#edit-' + model +'-alias').val('');
			$('#edit-' + model +'-rate').val('0.0');
			$('#edit-' + model +'-quantity').val('0.0');
			$('#edit-' + model +'-state').prop('checked', false);

			$('#modal-edit-' + model).foundation('reveal', 'close');
		}
	}, "json");

	return false;
});
{% endif %}


// Cancel Edit
{% if perms.catalog.change_category %}
$("body").delegate("[data-do='edit-currency-cancel']", "click", function(){

	model = 'currency';

	$('#edit-' + model + '-id').val('0');
	$('#edit-' + model + '-name').val('');
	$('#edit-' + model + '-fulle-name').val('');
	$('#edit-' + model + '-alias').val('');
	$('#edit-' + model + '-rate').val('0.0');
	$('#edit-' + model + '-quantity').val('0');
	$('#edit-' + model + '-state').prop('checked', false);

	$('#modal-edit-' + model).foundation('reveal', 'close');

	return false;
});
{% endif %}


// Open Delete
{% if perms.catalog.delete_currency %}
$("body").delegate("[data-do='open-delete-currency']", "click", function(){

	model = 'currency';

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
{% if perms.catalog.delete_currency %}
$("body").delegate("[data-do='delete-currency-apply']", "click", function(){

	model = 'currency';

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
{% if perms.catalog.delete_currency %}
$("body").delegate("[data-do='delete-currency-cancel']", "click", function(){

	model = 'currency';

	$('#delete-' + model + '-id').val(0);

	$('#modal-delete-' + model).foundation('reveal', 'close');

	return false;
});
{% endif %}


// Switch State
{% if perms.catalog.change_currency %}
$("body").delegate("[data-do='switch-currency-state']", "click", function(){

	model = 'currency';

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
