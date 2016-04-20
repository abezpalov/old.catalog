// Open New
{% if perms.catalog.add_category %}
$("body").delegate("[data-do='open-new-category']", "click", function(){

	model = 'category';

	$('#modal-edit-' + model + '-header').text('Добавить категорию');

	$('#edit-' + model + '-id').val('0');
	$('#edit-' + model + '-name').val('');
	$('#edit-' + model + '-alias').val('');
	$('#edit-' + model + '-parent').val('0');
	$('#edit-' + model + '-description').val('');
	$('#edit-' + model + '-state').prop('checked', false);

	$('#modal-edit-' + model).foundation('reveal', 'open');

	return false;
});
{% endif %}


// Open Edit
{% if perms.catalog.change_category %}
$("body").delegate("[data-do='open-edit-category']", "click", function(){

	model = 'category';

	$.post('/catalog/ajax/get/' + model + '/', {
		id : $(this).data(model + '-id'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {
		if ('success' == data.status){

			$('#modal-edit-' + model + '-header').text('Редактировать категорию');

			$('#edit-' + model + '-id').val(data[model]['id']);
			$('#edit-' + model + '-name').val(data[model]['name']);
			$('#edit-' + model + '-alias').val(data[model]['alias']);
			if (data[model]['parent']) {
				$('#edit-' + model + '-parent').val(data[model]['parent']['id']);
			} else {
				$('#edit-' + model + '-parent').val(0);
			}
			$('#edit-' + model + '-description').val(data[model]['description']);
			$('#edit-' + model + '-state').prop('checked', data[model]['state']);

			$('#modal-edit-' + model).foundation('reveal', 'open');
		}
	}, "json");

	return false;
});
{% endif %}


// Save
{% if perms.catalog.change_category %}
$("body").delegate("[data-do='edit-category-save']", "click", function(){

	model = 'category';

	$.post('/catalog/ajax/save/' + model + '/', {
		id          : $('#edit-' + model + '-id').val(),
		name        : $('#edit-' + model + '-name').val(),
		alias       : $('#edit-' + model + '-alias').val(),
		parent_id   : $('#edit-' + model + '-parent').val(),
		description : $('#edit-' + model + '-description').val(),
		state       : $('#edit-' + model + '-state').prop('checked'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {

		if ('success' == data.status){

			$('[data-' + model + '-name="' + data[model]['id'] + '"]').text(data[model]['name_leveled']);
			$('[data-' + model + '-state="' + data[model]['id'] + '"]').prop('checked', data[model]['state']);

			$('#edit-' + model + '-id').val('0');
			$('#edit-' + model + '-name').val('');
			$('#edit-' + model + '-alias').val('');
			$('#edit-' + model + '-parent').val('');
			$('#edit-' + model + '-description').val('');
			$('#edit-' + model + '-state').prop('checked', false);

			if (true == data.reload){
				setTimeout(function () {location.reload();}, 3000);
			}

			$('#modal-edit-' + model).foundation('reveal', 'close');
		}
	}, "json");

	return false;
});
{% endif %}


// Cancel Edit
{% if perms.catalog.change_category %}
$("body").delegate("[data-do='edit-category-cancel']", "click", function(){

	model = 'category';

	$('#edit-' + model + '-id').val('0');
	$('#edit-' + model + '-name').val('');
	$('#edit-' + model + '-alias').val('');
	$('#edit-' + model + '-parent').val('0');
	$('#edit-' + model + '-description').val('');
	$('#edit-' + model + '-state').prop('checked', false);

	$('#modal-edit-' + model).foundation('reveal', 'close');

	return false;
});
{% endif %}


// Open Delete
{% if perms.catalog.delete_category %}
$("body").delegate("[data-do='open-delete-category']", "click", function(){

	model = 'category';

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
{% if perms.catalog.delete_category %}
$("body").delegate("[data-do='delete-category-apply']", "click", function(){

	model = 'category';

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
{% if perms.catalog.delete_category %}
$("body").delegate("[data-do='delete-category-cancel']", "click", function(){

	model = 'category';

	$('#delete-' + model + '-id').val(0);

	$('#modal-delete-' + model).foundation('reveal', 'close');

	return false;
});
{% endif %}


// Switch State
{% if perms.catalog.change_category %}
$("body").delegate("[data-do='switch-category-state']", "click", function(){

	model = 'category';

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
