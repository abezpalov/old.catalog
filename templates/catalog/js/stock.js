{% if perms.catalog.add_stock %}
$("body").delegate("[data-do='open-new-stock']", "click", function(){

	model = 'stock';

	$('#modal-edit-' + model + '-header').text('Добавить склад');

	$('#edit-' + model + '-id').val('0');
	$('#edit-' + model + '-name').val('');
	$('#edit-' + model + '-delivery-time-min').val('');
	$('#edit-' + model + '-delivery-time-max').val('');
	$('#edit-' + model + '-alias').val('');
	$('#edit-' + model + '-state').prop('checked', true);

	$('#modal-edit-' + model).foundation('open');

	return false;
});
{% endif %}


{% if perms.catalog.change_stock %}
$("body").delegate("[data-do='open-edit-stock']", "click", function(){

	model = 'stock';

	$.post('/catalog/ajax/get/' + model + '/', {
		id : $(this).data(model + '-id'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {
		if ('success' == data.status){

			$('#modal-edit-' + model + '-header').text('Редактировать склад');

			$('#edit-' + model + '-id').val(data[model]['id']);
			$('#edit-' + model + '-name').val(data[model]['name']);
			$('#edit-' + model + '-delivery-time-min').val(data[model]['delivery_time_min']);
			$('#edit-' + model + '-delivery-time-max').val(data[model]['delivery_time_max']);
			$('#edit-' + model + '-alias').val(data[model]['alias']);
			$('#edit-' + model + '-state').prop('checked', data[model]['state']);

			$('#modal-edit-' + model).foundation('open');
		}
	}, "json");

	return false;
});
{% endif %}


{% if perms.catalog.change_stock %}
$("body").delegate("[data-do='edit-stock-save']", "click", function(){

	model = 'stock';

	$.post('/catalog/ajax/save/' + model + '/', {
		id                : $('#edit-' + model + '-id').val(),
		name              : $('#edit-' + model + '-name').val(),
		alias             : $('#edit-' + model + '-alias').val(),
		delivery_time_min : $('#edit-' + model + '-delivery-time-min').val(),
		delivery_time_max : $('#edit-' + model + '-delivery-time-max').val(),
		state             : $('#edit-' + model + '-state').prop('checked'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {

		if ('success' == data.status){

			$('[data-' + model + '-name="' + data[model]['id'] + '"]').text(data[model]['name']);
			$('[data-' + model + '-delivery-time-min="' + data[model]['id'] + '"]').text(data[model]['delivery_time_min']);
			$('[data-' + model + '-delivery-time-max="' + data[model]['id'] + '"]').text(data[model]['delivery_time_max']);
			$('[data-' + model + '-state="' + data[model]['id'] + '"]').prop('checked', data[model]['state']);

			$('#edit-' + model + '-id').val('0');
			$('#edit-' + model + '-name').val('');
			$('#edit-' + model + '-alias').val('');
			$('#edit-' + model + '-delivery-time-min').val('');
			$('#edit-' + model + '-delivery-time-max').val('');
			$('#edit-' + model + '-state').prop('checked', false);

			$('#modal-edit-' + model).foundation('close');
		}
	}, "json");

	return false;
});
{% endif %}


{% if perms.catalog.change_stock %}
$("body").delegate("[data-do='edit-stock-cancel']", "click", function(){

	model = 'stock';

	$('#edit-' + model + '-id').val('0');
	$('#edit-' + model + '-name').val('');
	$('#edit-' + model + '-name-short').val('');
	$('#edit-' + model + '-name-short-xml').val('');
	$('#edit-' + model + '-alias').val('');
	$('#edit-' + model + '-state').prop('checked', false);

	$('#modal-edit-' + model).foundation('close');

	return false;
});
{% endif %}


{% if perms.catalog.delete_stock %}
$("body").delegate("[data-do='open-delete-stock']", "click", function(){

	model = 'stock';

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


{% if perms.catalog.delete_stock %}
$("body").delegate("[data-do='delete-stock-apply']", "click", function(){

	model = 'stock';

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


{% if perms.catalog.delete_stock %}
$("body").delegate("[data-do='delete-stock-cancel']", "click", function(){

	model = 'stock';

	$('#delete-' + model + '-id').val(0);

	$('#modal-delete-' + model).foundation('close');

	return false;
});
{% endif %}


{% if perms.catalog.change_stock %}
$("body").delegate("[data-do='switch-stock-state']", "click", function(){

	model = 'stock';

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
