// Filter
$("body").delegate("[data-do='filter-parametersynonyms']", "click", function(){
	location.href = "/catalog/parametersynonyms/" + $("#filter-updater").val() + "/" + $("#filter-distributor").val() + "/" + $("#filter-parameter").val() + "/";
	return true;
});


// Open New
{% if perms.catalog.add_parametersynonym %}
$("body").delegate("[data-do='open-new-parametersynonym']", "click", function(){

	model_name = 'parametersynonym';

	$('#modal-edit-' + model_name + '-header').text('Добавить синоним параметра');

	$('#edit-' + model_name + '-id').val('0');
	$('#edit-' + model_name + '-name').val('');
	$('#edit-' + model_name + '-updater').val('0');
	$('#edit-' + model_name + '-distributor').val('0');
	$('#edit-' + model_name + '-parameter').val('0');

	$('#modal-edit-' + model_name).foundation('reveal', 'open');

	return false;
});
{% endif %}


// Open Edit
{% if perms.catalog.change_parametersynonym %}
$("body").delegate("[data-do='open-edit-parametersynonym']", "click", function(){

	model_name = 'parametersynonym';

	$.post('/catalog/ajax/get/' + model_name + '/', {
		id : $(this).data(model_name + '-id'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {
		if ('success' == data.status){

			$('#modal-edit-' + model_name + '-header').text('Редактировать синоним параметра');

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
			if (data[model_name]['parameter']) {
				$('#edit-' + model_name + '-parameter').val(data[model_name]['parameter']['id']);
			} else {
				$('#edit-' + model_name + '-parameter').val(0);
			}

			$('#modal-edit-' + model_name).foundation('reveal', 'open');

		}
	}, "json");

	return false;
});
{% endif %}


// Save
{% if perms.catalog.change_parametersynonym %}
$("body").delegate("[data-do='edit-parametersynonym-save']", "click", function(){

	model_name = 'parametersynonym';

	$.post('/catalog/ajax/save/' + model_name + '/', {
		id             : $('#edit-' + model_name + '-id').val(),
		name           : $('#edit-' + model_name + '-name').val(),
		updater_id     : $('#edit-' + model_name + '-updater').val(),
		distributor_id : $('#edit-' + model_name + '-distributor').val(),
		parameter_id   : $('#edit-' + model_name + '-parameter').val(),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {

		if ('success' == data.status){

			$('[data-' + model_name + '-name="' + data[model_name]['id'] + '"]').text(data[model_name]['name']);

			if (data[model_name]['updater']) {
				$('[data-' + model_name + '-updater-name="' + data[model_name]['id'] + '"]').text(data[model_name]['updater']['name']);
				$('[data-' + model_name + '-updater-name="' + data[model_name]['id'] + '"]').data('updater-id', data[model_name]['updater']['id']);
				$('[data-' + model_name + '-updater-name="' + data[model_name]['id'] + '"]').data('updater-name', data[model_name]['updater']['id']);
			} else {
				$('[data-' + model_name + '-updater-name="' + data[model_name]['id'] + '"]').text('');
				$('[data-' + model_name + '-updater-name="' + data[model_name]['id'] + '"]').data('updater-id', '0');
				$('[data-' + model_name + '-updater-name="' + data[model_name]['id'] + '"]').data('updater-name', '0');
			}

			if (data[model_name]['distributor']) {
				$('[data-' + model_name + '-distributor-name="' + data[model_name]['id'] + '"]').text(data[model_name]['distributor']['name']);
				$('[data-' + model_name + '-distributor-name="' + data[model_name]['id'] + '"]').data('distributor-id', data[model_name]['distributor']['id']);
				$('[data-' + model_name + '-distributor-name="' + data[model_name]['id'] + '"]').data('distributor-name', data[model_name]['distributor']['id']);
			} else {
				$('[data-' + model_name + '-distributor-name="' + data[model_name]['id'] + '"]').text('');
				$('[data-' + model_name + '-distributor-name="' + data[model_name]['id'] + '"]').data('distributor-id', '0');
				$('[data-' + model_name + '-distributor-name="' + data[model_name]['id'] + '"]').data('distributor-name', '0');
			}

			if (data[model_name]['parameter']) {
				$('[data-' + model_name + '-parameter-name="' + data[model_name]['id'] + '"]').text(data[model_name]['parameter']['name']);
				$('[data-' + model_name + '-parameter-name="' + data[model_name]['id'] + '"]').data('parameter-id', data[model_name]['parameter']['id']);
				$('[data-' + model_name + '-parameter-name="' + data[model_name]['id'] + '"]').data('parameter-name', data[model_name]['parameter']['id']);
			} else {
				$('[data-' + model_name + '-parameter-name="' + data[model_name]['id'] + '"]').text('');
				$('[data-' + model_name + '-parameter-name="' + data[model_name]['id'] + '"]').data('parameter-id', '0');
				$('[data-' + model_name + '-parameter-name="' + data[model_name]['id'] + '"]').data('parameter-name', '0');
			}

			$('#edit-' + model_name + '-id').val('0');
			$('#edit-' + model_name + '-name').val('');
			$('#edit-' + model_name + '-updater').val('0');
			$('#edit-' + model_name + '-distributor').val('0');
			$('#edit-' + model_name + '-parameter').val('0');

			$('#modal-edit-' + model_name).foundation('reveal', 'close');
		}
	}, "json");

	return false;
});
{% endif %}


// Cancel Edit
{% if perms.catalog.change_parametersynonym %}
$("body").delegate("[data-do='edit-parametersynonym-cancel']", "click", function(){

	model_name = 'categorysynonym';


	$('#edit-' + model_name + '-id').val('0');
	$('#edit-' + model_name + '-name').val('');
	$('#edit-' + model_name + '-updater').val('0');
	$('#edit-' + model_name + '-distributor').val('0');
	$('#edit-' + model_name + '-parameter').val('0');

	$('#modal-edit-' + model_name).foundation('reveal', 'close');

	return false;
});
{% endif %}


// Open Delete
{% if perms.catalog.delete_parametersynonym %}
$("body").delegate("[data-do='open-delete-parametersynonym']", "click", function(){

	model_name = 'parametersynonym';

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
{% if perms.catalog.delete_parametersynonym %}
$("body").delegate("[data-do='delete-parametersynonym-apply']", "click", function(){

	model_name = 'parametersynonym';

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
{% if perms.catalog.delete_parametersynonym %}
$("body").delegate("[data-do='delete-parametersynonym-cancel']", "click", function(){

	model_name = 'parametersynonym';

	$('#delete-' + model_name + '-id').val(0);

	$('#modal-delete-' + model_name).foundation('reveal', 'close');

	return false;
});
{% endif %}


// Link Same Foreign
$("body").delegate("[data-do='link-parametersynonym-same-parameter']", "click", function(){

	model_name   = 'parametersynonym';
	foreign_name = 'parameter';

	parameter_synonym_id = $(this).data('id');
	$.post('/catalog/ajax/link/' + model_name + '/same/' + foreign_name + '/', {
		id : $(this).data(model_name + '-id'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {
		if ('succes' == data.status) {

			$('[data-' + model_name + '-id="' + parameter_synonym_id + '"]').text(data[model_name]['name']);
			$('[data-' + model_name + '-id="' + parameter_synonym_id + '"]').data('id', data[model_name]['id']);
			$('[data-' + model_name + '-id="' + parameter_synonym_id + '"]').data('parameter-name', data[model_name]['id']);

			// TODO
		}
	}, "json");
	return false;
});
