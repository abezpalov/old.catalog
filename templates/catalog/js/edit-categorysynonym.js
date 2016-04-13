// Filter
$("body").delegate("[data-do='filter-categorysynonyms']", "click", function(){
	location.href = "/catalog/categorysynonyms/" + $("#filter-updater").val() + "/" + $("#filter-distributor").val() + "/" + $("#filter-category").val() + "/";
	return true;
});


// Open New
{% if perms.catalog.add_categorysynonym %}
$("body").delegate("[data-do='open-new-categorysynonym']", "click", function(){

	model_name = 'categorysynonym';

	$('#modal-edit-' + model_name + '-header').text('Добавить синоним категории');

	$('#edit-' + model_name + '-id').val('0');
	$('#edit-' + model_name + '-name').val('');
	$('#edit-' + model_name + '-updater').val('0');
	$('#edit-' + model_name + '-distributor').val('0');
	$('#edit-' + model_name + '-category').val('0');

	$('#modal-edit-' + model_name).foundation('reveal', 'open');

	return false;
});
{% endif %}


// Open Edit
{% if perms.catalog.change_categorysynonym %}
$("body").delegate("[data-do='open-edit-categorysynonym']", "click", function(){

	model_name = 'categorysynonym';

	$.post('/catalog/ajax/get/' + model_name + '/', {
		id : $(this).data(model_name + '-id'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {
		if ('success' == data.status){

			$('#modal-edit-' + model_name + '-header').text('Редактировать синоним категории');

			$('#edit-' + model_name + '-id').val(data[model_name]['id']);
			$('#edit-' + model_name + '-name').val(data[model_name]['name'])
			if (data[model_name]['updater']) {
				$('#edit-' + model_name + '-updater').val(data[model_name]['updater']['id']);
			} else {
				$('#edit-' + model_name + '-updater').val(0);
			}
			if (data[model_name]['distributor']) {
				$('#edit-' + model_name + '-distributor').val(data[model_name]['distributor']['id']);
			} else {
				$('#edit-' + model_name + '-distributor').val(0);
			}
			if (data[model_name]['category']) {
				$('#edit-' + model_name + '-category').val(data[model_name]['category']['id']);
			} else {
				$('#edit-' + model_name + '-category').val(0);
			}
			$('#modal-edit-categorysynonym').foundation('reveal', 'open');
		}
	}, "json");

	return false;
});
{% endif %}


// Save
{% if perms.catalog.change_categorysynonym %}
$("body").delegate("[data-do='edit-categorysynonym-save']", "click", function(){

	model_name = 'categorysynonym';

	$.post('/catalog/ajax/save/' + model_name + '/', {
		id             : $('#edit-' + model_name + '-id').val(),
		name           : $('#edit-' + model_name + '-name').val(),
		updater_id     : $('#edit-' + model_name + '-updater').val(),
		distributor_id : $('#edit-' + model_name + '-distributor').val(),
		category_id    : $('#edit-' + model_name + '-category').val(),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {

		if ('success' == data.status){

			$('[data-' + model_name + '-name="' + data[model_name]['id'] + '"]').text(data[model_name]['name']);

			if (data[model_name]['updater']) {
				$('[data-' + model_name + '-updater-name="' + data[model_name]['id'] + '"]').text(data[model_name]['updater']['name']);
				$('[data-' + model_name + '-updater-name="' + data[model_name]['id'] + '"]').data('updater-name', data[model_name]['updater']['id']);
			} else {
				$('[data-' + model_name + '-updater-name="' + data[model_name]['id'] + '"]').text('');
				$('[data-' + model_name + '-updater-name="' + data[model_name]['id'] + '"]').data('updater-name', '0');
			}

			if (data[model_name]['distributor']) {
				$('[data-' + model_name + '-distributor-name="' + data[model_name]['id'] + '"]').text(data[model_name]['distributor']['name']);
				$('[data-' + model_name + '-distributor-name="' + data[model_name]['id'] + '"]').data('distributor-name', data[model_name]['distributor']['id']);
			} else {
				$('[data-' + model_name + '-distributor-name="' + data[model_name]['id'] + '"]').text('');
				$('[data-' + model_name + '-distributor-name="' + data[model_name]['id'] + '"]').data('distributor-name', '0');
			}

			if (data[model_name]['category']) {
				$('[data-' + model_name + '-category-name="' + data[model_name]['id'] + '"]').text(data[model_name]['category']['name']);
				$('[data-' + model_name + '-category-name="' + data[model_name]['id'] + '"]').data('category-name', data[model_name]['category']['id']);
			} else {
				$('[data-' + model_name + '-category-name="' + data[model_name]['id'] + '"]').text('');
				$('[data-' + model_name + '-category-name="' + data[model_name]['id'] + '"]').data('category-name', '0');
			}

			$('#edit-' + model_name + '-id').val('0');
			$('#edit-' + model_name + '-name').val('');
			$('#edit-' + model_name + '-updater').val('0');
			$('#edit-' + model_name + '-distributor').val('0');
			$('#edit-' + model_name + '-category').val('0');

			$('#modal-edit-categorysynonym').foundation('reveal', 'close');
		}
	}, "json");

	return false;
});
{% endif %}


// Cancel Edit
{% if perms.catalog.change_categorysynonym %}
$("body").delegate("[data-do='edit-categorysynonym-cancel']", "click", function(){

	model_name = 'categorysynonym';


	$('#edit-' + model_name + '-id').val('0');
	$('#edit-' + model_name + '-name').val('');
	$('#edit-' + model_name + '-updater').val('0');
	$('#edit-' + model_name + '-distributor').val('0');
	$('#edit-' + model_name + '-category').val('0');

	$('#modal-edit-' + model_name).foundation('reveal', 'close');

	return false;
});
{% endif %}


// Open Delete
{% if perms.catalog.delete_categorysynonym %}
$("body").delegate("[data-do='open-delete-categorysynonym']", "click", function(){

	model_name = 'categorysynonym';

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
{% if perms.catalog.delete_categorysynonym %}
$("body").delegate("[data-do='delete-categorysynonym-apply']", "click", function(){

	model_name = 'categorysynonym';

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
