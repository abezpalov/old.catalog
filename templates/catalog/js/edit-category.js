// Open New
{% if perms.catalog.add_category %}
$("body").delegate("[data-do='open-new-category']", "click", function(){

	model_name = 'category';

	$('#modal-edit-' + model_name + '-header').text('Добавить категорию');

	$('#edit-' + model_name + '-id').val('0');
	$('#edit-' + model_name + '-name').val('');
	$('#edit-' + model_name + '-alias').val('');
	$('#edit-' + model_name + '-parent').val('0');
	$('#edit-' + model_name + '-description').val('');
	$('#edit-' + model_name + '-state').prop('checked', false);

	$('#modal-edit-' + model_name).foundation('reveal', 'open');

	return false;
});
{% endif %}


// Open Edit
{% if perms.catalog.change_category %}
$("body").delegate("[data-do='open-edit-category']", "click", function(){

	model_name = 'category';

	$.post('/catalog/ajax/get/' + model_name + '/', {
		id : $(this).data(model_name + '-id'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {
		if ('success' == data.status){

			$('#modal-edit-' + model_name + '-header').text('Редактировать категорию');

			$('#edit-' + model_name + '-id').val(data[model_name]['id']);
			$('#edit-' + model_name + '-name').val(data[model_name]['name']);
			$('#edit-' + model_name + '-alias').val(data[model_name]['alias']);
			if (data[model_name]['parent']) {
				$('#edit-' + model_name + '-parent').val(data[model_name]['parent']['id']);
			} else {
				$('#edit-' + model_name + '-parent').val(0);
			}
			$('#edit-' + model_name + '-description').val(data[model_name]['description']);
			$('#edit-' + model_name + '-state').prop('checked', data[model_name]['state']);

			$('#modal-edit-' + model_name).foundation('reveal', 'open');
		}
	}, "json");

	return false;
});
{% endif %}


// Save
{% if perms.catalog.change_category %}
$("body").delegate("[data-do='edit-category-save']", "click", function(){

	model_name = 'category';

	$.post('/catalog/ajax/save/' + model_name + '/', {
		id          : $('#edit-' + model_name + '-id').val(),
		name        : $('#edit-' + model_name + '-name').val(),
		alias       : $('#edit-' + model_name + '-alias').val(),
		parent_id   : $('#edit-' + model_name + '-parent').val(),
		description : $('#edit-' + model_name + '-description').val(),
		state       : $('#edit-' + model_name + '-state').prop('checked'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {

		if ('success' == data.status){

			$('[data-' + model_name + '-name="' + data[model_name]['id'] + '"]').text(data[model_name]['name_leveled']);
			$('[data-' + model_name + '-state="' + data[model_name]['id'] + '"]').prop('checked', data[model_name]['state']);

			$('#edit-' + model_name + '-id').val('0');
			$('#edit-' + model_name + '-name').val('');
			$('#edit-' + model_name + '-alias').val('');
			$('#edit-' + model_name + '-parent').val('');
			$('#edit-' + model_name + '-description').val('');
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
{% if perms.catalog.change_category %}
$("body").delegate("[data-do='edit-category-cancel']", "click", function(){

	model_name = 'category';

	$('#edit-' + model_name + '-id').val('0');
	$('#edit-' + model_name + '-name').val('');
	$('#edit-' + model_name + '-alias').val('');
	$('#edit-' + model_name + '-parent').val('0');
	$('#edit-' + model_name + '-description').val('');
	$('#edit-' + model_name + '-state').prop('checked', false);

	$('#modal-edit-' + model_name).foundation('reveal', 'close');

	return false;
});
{% endif %}


// Open Delete
{% if perms.catalog.delete_category %}
$("body").delegate("[data-do='open-delete-category']", "click", function(){

	model_name = 'category';

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
{% if perms.catalog.delete_category %}
$("body").delegate("[data-do='delete-category-apply']", "click", function(){

	model_name = 'category';

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
{% if perms.catalog.delete_category %}
$("body").delegate("[data-do='delete-category-cancel']", "click", function(){

	model_name = 'category';

	$('#delete-' + model_name + '-id').val(0);

	$('#modal-delete-' + model_name).foundation('reveal', 'close');

	return false;
});
{% endif %}


// Switch State
{% if perms.catalog.change_category %}
$("body").delegate("[data-do='switch-category-state']", "click", function(){

	model_name = 'category';

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
