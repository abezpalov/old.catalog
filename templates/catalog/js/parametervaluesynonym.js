{% if perms.catalog.add_parametervaluesynonym or perms.catalog.change_parametervaluesynonym or perms.catalog.delete_parametervaluesynonym %}
$("body").delegate("[data-do='filter-parametervaluesynonyms']", "change", function(){
	location.href = "/catalog/parametervaluesynonyms/" + $("#filter-updater").val() + "/" + $("#filter-parameter").val() + "/";
	return true;
});
{% endif %}

{% if perms.catalog.add_parametervaluesynonym %}
$("body").delegate("[data-do='open-new-parametervaluesynonym']", "click", function(){

	model = 'parametervaluesynonym';

	$('#modal-edit-' + model + '-header').text('Добавить синоним значения параметра');

	$('#edit-' + model + '-id').val('0');
	$('#edit-' + model + '-name').val('');
	$('#edit-' + model + '-updater').val('0');
	$('#edit-' + model + '-parameter').val('0');
	$('#edit-' + model + '-parametervalue').val('0');

	$('#modal-edit-' + model).foundation('reveal', 'open');

	return false;
});
{% endif %}


{% if perms.catalog.change_parametervaluesynonym %}
$("body").delegate("[data-do='open-edit-parametervaluesynonym']", "click", function(){

	model = 'parametervaluesynonym';

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
			if (data[model]['parameter']) {
				$('#edit-' + model + '-parameter').val(data[model]['parameter']['id']);
			} else {
				$('#edit-' + model + '-parameter').val(0);
			}
			if (data[model]['parametervalue']) {
				$('#edit-' + model + '-parametervalue').val(data[model]['parametervalue']['id']);
			} else {
				$('#edit-' + model + '-parametervalue').val(0);
			}

			$('#modal-edit-' + model).foundation('reveal', 'open');

		}
	}, "json");

	return false;
});
{% endif %}


{% if perms.catalog.change_parametervaluesynonym %}
$("body").delegate("[data-do='edit-parametervaluesynonym-save']", "click", function(){

	model = 'parametervaluesynonym';

	$.post('/catalog/ajax/save/' + model + '/', {
		id                : $('#edit-' + model + '-id').val(),
		name              : $('#edit-' + model + '-name').val(),
		updater_id        : $('#edit-' + model + '-updater').val(),
		parameter_id      : $('#edit-' + model + '-parameter').val(),
		parametervalue_id : $('#edit-' + model + '-parameter').val(),
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

			if (data[model]['parameter']) {
				$('[data-' + model + '-parameter-name="' + data[model]['id'] + '"]').text(data[model]['parameter']['name']);
				$('[data-' + model + '-parameter-name="' + data[model]['id'] + '"]').data('parameter-id', data[model]['parameter']['id']);
				$('[data-' + model + '-parameter-name="' + data[model]['id'] + '"]').data('parameter-name', data[model]['parameter']['id']);
			} else {
				$('[data-' + model + '-parameter-name="' + data[model]['id'] + '"]').text('');
				$('[data-' + model + '-parameter-name="' + data[model]['id'] + '"]').data('parameter-id', '0');
				$('[data-' + model + '-parameter-name="' + data[model]['id'] + '"]').data('parameter-name', '0');
			}

			if (data[model]['parametervalue']) {
				$('[data-' + model + '-parametervalue-name="' + data[model]['id'] + '"]').text(data[model]['parametervalue']['name']);
				$('[data-' + model + '-parametervalue-name="' + data[model]['id'] + '"]').data('parametervalue-id', data[model]['parametervalue']['id']);
				$('[data-' + model + '-parametervalue-name="' + data[model]['id'] + '"]').data('parametervalue-name', data[model]['parametervalue']['id']);
			} else {
				$('[data-' + model + '-parametervalue-name="' + data[model]['id'] + '"]').text('');
				$('[data-' + model + '-parametervalue-name="' + data[model]['id'] + '"]').data('parametervalue-id', '0');
				$('[data-' + model + '-parametervalue-name="' + data[model]['id'] + '"]').data('parametervalue-name', '0');
			}

			$('#edit-' + model + '-id').val('0');
			$('#edit-' + model + '-name').val('');
			$('#edit-' + model + '-updater').val('0');
			$('#edit-' + model + '-parameter').val('0');
			$('#edit-' + model + '-parametervalue').val('0');

			$('#modal-edit-' + model).foundation('reveal', 'close');
		}
	}, "json");

	return false;
});
{% endif %}


{% if perms.catalog.change_parametervaluesynonym %}
$("body").delegate("[data-do='edit-parametervaluesynonym-cancel']", "click", function(){

	model = 'parametervaluesynonym';


	$('#edit-' + model + '-id').val('0');
	$('#edit-' + model + '-name').val('');
	$('#edit-' + model + '-updater').val('0');
	$('#edit-' + model + '-parameter').val('0');
	$('#edit-' + model + '-parametervalue').val('0');

	$('#modal-edit-' + model).foundation('reveal', 'close');

	return false;
});
{% endif %}


{% if perms.catalog.delete_parametervaluesynonym %}
$("body").delegate("[data-do='open-delete-parametervaluesynonym']", "click", function(){

	model = 'parametervaluesynonym';

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


{% if perms.catalog.delete_parametervaluesynonym %}
$("body").delegate("[data-do='delete-parametervaluesynonym-apply']", "click", function(){

	model = 'parametervaluesynonym';

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


{% if perms.catalog.delete_parametervaluesynonym %}
$("body").delegate("[data-do='delete-parametervaluesynonym-cancel']", "click", function(){

	model = 'parametervaluesynonym';

	$('#delete-' + model + '-id').val(0);

	$('#modal-delete-' + model).foundation('reveal', 'close');

	return false;
});
{% endif %}


{% if perms.catalog.change_parametervaluesynonym %}
$("body").delegate("[data-do='link-parametervaluesynonym-same-parametervalue']", "click", function(){

	model = 'parametervaluesynonym';
	foreign = 'parametervalue';

	$.post('/catalog/ajax/link/' + model + '/same/' + foreign + '/', {
		id : $(this).data(model + '-id'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {
		if ('success' == data.status) {

			$('[data-' + model + '-' + foreign + '-name="' + data[model]['id'] + '"]').text(data[model][foreign]['name']);
			$('[data-' + model + '-' + foreign + '-name="' + data[model]['id'] + '"]').data(foreign + '-id', data[model][foreign]['id']);
			$('[data-' + model + '-' + foreign + '-name="' + data[model]['id'] + '"]').data(foreign + '-name', data[model][foreign]['id']);

			// TODO Обновляем список производителей в окне редактирования синонимов
		}
	}, "json");
	return false;
});
{% endif %}
