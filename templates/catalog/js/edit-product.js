// Open Edit
{% if perms.catalog.change_product %}
$("body").delegate("[data-do='open-edit-product']", "click", function(){

	model_name = 'product';

	$.post('/catalog/ajax/get/' + model_name + '/', {
		id : $(this).data(model_name + '-id'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {
		if ('success' == data.status){

			$('#modal-edit-' + model_name + '-header').text('Редактировать продукт');

			$('#edit-' + model_name + '-id').val(data[model_name]['id']);
			$('#edit-' + model_name + '-name').val(data[model_name]['name']);
			$('#edit-' + model_name + '-article').val(data[model_name]['article']);
			if (data[model_name]['vendor']) {
				$('#edit-' + model_name + '-vendor').val(data[model_name]['vendor']['id']);
			} else {
				$('#edit-' + model_name + '-vendor').val(0);
			}
			if (data[model_name]['category']) {
				$('#edit-' + model_name + '-category').val(data[model_name]['category']['id']);
			} else {
				$('#edit-' + model_name + '-category').val(0);
			}
			$('#edit-' + model_name + '-description').val(data[model_name]['description']);
			if (data[model_name]['double']) {
				$('#edit-' + model_name + '-double').val(data[model_name]['double']['id']);
			} else {
				$('#edit-' + model_name + '-double').val(0);
			}
			$('#edit-' + model_name + '-state').prop('checked', data[model_name]['state']);

			$('#modal-edit-' + model_name).foundation('reveal', 'open');
		}
	}, "json");

	return false;
});
{% endif %}


// Save
{% if perms.catalog.change_product %}
$("body").delegate("[data-do='edit-product-save']", "click", function(){

	model_name = 'product';

	$.post("/catalog/ajax/save-product/", {
		id          : $('#edit-' + model_name + '-id').val(),
		name        : $('#edit-' + model_name + '-name').val(),
		article     : $('#edit-' + model_name + '-article').val(),
		vendor_id   : $('#edit-' + model_name + '-vendor').val(),
		category_id : $('#edit-' + model_name + '-category').val(),
		description : $('#edit-' + model_name + '-description').val(),
		duble_id    : $('#edit-' + model_name + '-double').val(),
		state       : $('#edit-' + model_name + '-state').prop('checked'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {

		if ('success' == data.status){

			$('[data-' + model_name + '-name="' + data[model_name]['id'] + '"]').text(data[model_name]['name']);
			$('[data-' + model_name + '-article="' + data[model_name]['id'] + '"]').text(data[model_name]['article']);
			$('[data-' + model_name + '-state="' + data[model_name]['id'] + '"]').prop('checked', data[model_name]['state']);

			$('#edit-' + model_name + '-id').val('0');
			$('#edit-' + model_name + '-name').val('');
			$('#edit-' + model_name + '-article').val('');
			$('#edit-' + model_name + '-vendor').val(0);
			$('#edit-' + model_name + '-category').val(0);
			$('#edit-' + model_name + '-description').val('');
			$('#edit-' + model_name + '-double').val(0);
			$('#edit-' + model_name + '-state').prop('checked', false);

			if (true == data.reload){
				setTimeout(function () {location.reload();}, 3000);
			}

			$('#modal-edit-' + model_name).foundation('reveal', 'close');

		}
	}, "json");

	return false;
});
{% endif %}


// Cancel Edit
{% if perms.catalog.change_product %}
$("body").delegate("[data-do='edit-product-cancel']", "click", function(){

	model_name = 'product';

	$('#edit-' + model_name + '-id').val('0');
	$('#edit-' + model_name + '-name').val('')
	$('#edit-' + model_name + '-article').val('')
	$('#edit-' + model_name + '-vendor').val('0')
	$('#edit-' + model_name + '-category').val('0')
	$('#edit-' + model_name + '-description').val('')
	$('#edit-' + model_name + '-double').val('')
	$('#edit-' + model_name + '-state').prop('checked', false)

	$('#modal-edit-' + model_name).foundation('reveal', 'close');

	return false;
});
{% endif %}


// Open Delete
{% if perms.catalog.delete_product %}
$("body").delegate("[data-do='open-delete-product']", "click", function(){

	model_name = 'product';

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
{% if perms.catalog.delete_product %}
$("body").delegate("[data-do='delete-product-apply']", "click", function(){

	model_name = 'product';

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
{% if perms.catalog.delete_product %}
$("body").delegate("[data-do='delete-product-cancel']", "click", function(){

	model_name = 'product';

	$('#delete-' + model_name + '-id').val(0);

	$('#modal-delete-' + model_name).foundation('reveal', 'close');

	return false;
});
{% endif %}


// Switch State
{% if perms.catalog.change_product %}
$("body").delegate("[data-do='switch-product-state']", "click", function(){

	model_name = 'product';

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
