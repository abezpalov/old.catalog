// Filter
$("body").delegate("[data-do='filter-parametersynonyms']", "click", function(){
	location.href = "/catalog/parametersynonyms/" + $("#filter-updater").val() + "/" + $("#filter-distributor").val() + "/" + $("#filter-parameter").val() + "/";
	return true;
});


// Open New
{% if perms.catalog.add_parametersynonym %}
$("body").delegate("[data-do='open-new-parametersynonym']", "click", function(){

	model = 'parametersynonym';

	$('#modal-edit-' + model + '-header').text('Добавить синоним параметра');

	$('#edit-' + model + '-id').val('0');
	$('#edit-' + model + '-name').val('');
	$('#edit-' + model + '-updater').val('0');
	$('#edit-' + model + '-distributor').val('0');
	$('#edit-' + model + '-parameter').val('0');

	$('#modal-edit-' + model).foundation('reveal', 'open');

	return false;
});
{% endif %}


// Open Edit
{% if perms.catalog.change_parametersynonym %}
$("body").delegate("[data-do='open-edit-parametersynonym']", "click", function(){

	model = 'parametersynonym';

	$.post('/catalog/ajax/get/' + model + '/', {
		id : $(this).data(model + '-id'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {
		if ('success' == data.status){

			$('#modal-edit-' + model + '-header').text('Редактировать синоним параметра');

			$('#edit-' + model + '-id').val(data[model]['id']);
			$('#edit-' + model + '-name').val(data[model]['name'])
			if (data[model]['updater']) {
				$('#edit-' + model + '-updater').val(data[model]['updater']['id']);
			} else {
				$('#edit-' + model + '-updater').val(0);
			}
			if (data[model]['distributor']) {
				$('#edit-' + model + '-distributor').val(data[model]['distributor']['id']);
			} else {
				$('#edit-' + model + '-distributor').val(0);
			}
			if (data[model]['parameter']) {
				$('#edit-' + model + '-parameter').val(data[model]['parameter']['id']);
			} else {
				$('#edit-' + model + '-parameter').val(0);
			}

			$('#modal-edit-' + model).foundation('reveal', 'open');

		}
	}, "json");

	return false;
});
{% endif %}


// Save
{% if perms.catalog.change_parametersynonym %}
$("body").delegate("[data-do='edit-parametersynonym-save']", "click", function(){

	model = 'parametersynonym';

	$.post('/catalog/ajax/save/' + model + '/', {
		id             : $('#edit-' + model + '-id').val(),
		name           : $('#edit-' + model + '-name').val(),
		updater_id     : $('#edit-' + model + '-updater').val(),
		distributor_id : $('#edit-' + model + '-distributor').val(),
		parameter_id   : $('#edit-' + model + '-parameter').val(),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {

		if ('success' == data.status){

			$('[data-' + model + '-name="' + data[model]['id'] + '"]').text(data[model]['name']);

			if (data[model]['updater']) {
				$('[data-' + model + '-updater-name="' + data[model]['id'] + '"]').text(data[model]['updater']['name']);
				$('[data-' + model + '-updater-name="' + data[model]['id'] + '"]').data('updater-id', data[model]['updater']['id']);
				$('[data-' + model + '-updater-name="' + data[model]['id'] + '"]').data('updater-name', data[model]['updater']['id']);
			} else {
				$('[data-' + model + '-updater-name="' + data[model]['id'] + '"]').text('');
				$('[data-' + model + '-updater-name="' + data[model]['id'] + '"]').data('updater-id', '0');
				$('[data-' + model + '-updater-name="' + data[model]['id'] + '"]').data('updater-name', '0');
			}

			if (data[model]['distributor']) {
				$('[data-' + model + '-distributor-name="' + data[model]['id'] + '"]').text(data[model]['distributor']['name']);
				$('[data-' + model + '-distributor-name="' + data[model]['id'] + '"]').data('distributor-id', data[model]['distributor']['id']);
				$('[data-' + model + '-distributor-name="' + data[model]['id'] + '"]').data('distributor-name', data[model]['distributor']['id']);
			} else {
				$('[data-' + model + '-distributor-name="' + data[model]['id'] + '"]').text('');
				$('[data-' + model + '-distributor-name="' + data[model]['id'] + '"]').data('distributor-id', '0');
				$('[data-' + model + '-distributor-name="' + data[model]['id'] + '"]').data('distributor-name', '0');
			}

			if (data[model]['parameter']) {
				$('[data-' + model + '-parameter-name="' + data[model]['id'] + '"]').text(data[model]['parameter']['name']);
				$('[data-' + model + '-parameter-name="' + data[model]['id'] + '"]').data('parameter-id', data[model]['parameter']['id']);
				$('[data-' + model + '-parameter-name="' + data[model]['id'] + '"]').data('parameter-name', data[model]['parameter']['id']);
			} else {
				$('[data-' + model + '-parameter-name="' + data[model]['id'] + '"]').text('');
				$('[data-' + model + '-parameter-name="' + data[model]['id'] + '"]').data('parameter-id', '0');
				$('[data-' + model + '-parameter-name="' + data[model]['id'] + '"]').data('parameter-name', '0');
			}

			$('#edit-' + model + '-id').val('0');
			$('#edit-' + model + '-name').val('');
			$('#edit-' + model + '-updater').val('0');
			$('#edit-' + model + '-distributor').val('0');
			$('#edit-' + model + '-parameter').val('0');

			$('#modal-edit-' + model).foundation('reveal', 'close');
		}
	}, "json");

	return false;
});
{% endif %}


// Cancel Edit
{% if perms.catalog.change_parametersynonym %}
$("body").delegate("[data-do='edit-parametersynonym-cancel']", "click", function(){

	model = 'categorysynonym';


	$('#edit-' + model + '-id').val('0');
	$('#edit-' + model + '-name').val('');
	$('#edit-' + model + '-updater').val('0');
	$('#edit-' + model + '-distributor').val('0');
	$('#edit-' + model + '-parameter').val('0');

	$('#modal-edit-' + model).foundation('reveal', 'close');

	return false;
});
{% endif %}


// Open Delete
{% if perms.catalog.delete_parametersynonym %}
$("body").delegate("[data-do='open-delete-parametersynonym']", "click", function(){

	model = 'parametersynonym';

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
{% if perms.catalog.delete_parametersynonym %}
$("body").delegate("[data-do='delete-parametersynonym-apply']", "click", function(){

	model = 'parametersynonym';

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
{% if perms.catalog.delete_parametersynonym %}
$("body").delegate("[data-do='delete-parametersynonym-cancel']", "click", function(){

	model = 'parametersynonym';

	$('#delete-' + model + '-id').val(0);

	$('#modal-delete-' + model).foundation('reveal', 'close');

	return false;
});
{% endif %}


// Link Same Foreign
$("body").delegate("[data-do='link-parametersynonym-same-parameter']", "click", function(){

	model   = 'parametersynonym';
	foreign_name = 'parameter';

	parameter_synonym_id = $(this).data('id');
	$.post('/catalog/ajax/link/' + model + '/same/' + foreign_name + '/', {
		id : $(this).data(model + '-id'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {
		if ('succes' == data.status) {

			$('[data-' + model + '-id="' + parameter_synonym_id + '"]').text(data[model]['name']);
			$('[data-' + model + '-id="' + parameter_synonym_id + '"]').data('id', data[model]['id']);
			$('[data-' + model + '-id="' + parameter_synonym_id + '"]').data('parameter-name', data[model]['id']);

			// TODO
		}
	}, "json");
	return false;
});
