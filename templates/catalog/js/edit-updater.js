{% if perms.catalog.change_updater %}
$("body").delegate("[data-do='open-edit-updater']", "click", function(){

	model_name = 'updater'

	$.post('/catalog/ajax/get/' + model_name + '/', {
		id : $(this).data('id'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {
		if ('success' == data.status){

			$('#modal-edit-' + model_name + '-header').text('Редактировать загрузчик');
			$('#edit-' + model_name + '-id').val(data[model_name]['id']);
			$('#edit-' + model_name + '-name').val(data[model_name]['name']);
			$('#edit-' + model_name + '-alias').val(data[model_name]['alias']);
			$('#edit-' + model_name + '-login').val(data[model_name]['login']);
			$('#edit-' + model_name + '-password').val(data[model_name]['password']);
			$('#edit-' + model_name + '-state').prop('checked', data[model_name]['state']);

			$('#modal-edit-' + model_name).foundation('reveal', 'open');
		}
	}, "json");
	return false;
});
{% endif %}


{% if perms.catalog.change_updater %}
$("body").delegate("[data-do='edit-updater-save']", "click", function(){

	model_name = 'updater'

	$.post('/catalog/ajax/save/' + model_name + '/', {
		id       : $('#edit-' + model_name + '-id').val(),
		name     : $('#edit-' + model_name + '-name').val(),
		alias    : $('#edit-' + model_name + '-alias').val(),
		login    : $('#edit-' + model_name + '-login').val(),
		password : $('#edit-' + model_name + '-password').val(),
		state    : $('#edit-' + model_name + '-state').prop('checked'),
		csrfmiddlewaretoken: '{{ csrf_token }}'
	},
	function(data) {
		if ('success' == data.status){

			$("[data-" + model_name + "-name='" + $('#edit-' + model_name + '-id').val() + "']").text(data[model_name]['name']);
			$("[data-" + model_name + "-state='" + $('#edit-' + model_name + '-id').val() + "']").prop('checked', data[model_name]['state']);

			$('#edit-' + model_name + '-id').val('0');
			$('#edit-' + model_name + '-name').val('');
			$('#edit-' + model_name + '-alias').val('');
			$('#edit-' + model_name + '-login').val('');
			$('#edit-' + model_name + '-password').val('');
			$('#edit-' + model_name + '-state').prop('checked', false);

			$('#modal-edit-' + model_name).foundation('reveal', 'close');
		}
	}, "json");
	return false;
});
{% endif %}


{% if perms.catalog.change_updater %}
$("body").delegate("[data-do='edit-updater-cancel']", "click", function(){

	model_name = 'updater'

	$('#edit-' + model_name + '-id').val('0');
	$('#edit-' + model_name + '-name').val('');
	$('#edit-' + model_name + '-alias').val('');
	$('#edit-' + model_name + '-login').val('');
	$('#edit-' + model_name + '-password').val('');
	$('#edit-' + model_name + '-state').prop('checked', false);

	$('#modal-edit-' + model_name).foundation('reveal', 'close');

	return false;
});
{% endif %}


{% if perms.catalog.delete_updater %}
$("body").delegate("[data-do='open-delete-updater']", "click", function(){

	model_name = 'updater'

	$('#delete-' + model_name + '-id').val($(this).data('id'));

	$('#modal-delete-' + model_name).foundation('reveal', 'open');

	return false;
});
{% endif %}


{% if perms.catalog.delete_updater %}
$("body").delegate("[data-do='trash-updater']", "click", function(){

	model_name = 'updater'

	$.post('/catalog/ajax/delete/' + model_name + '/', {
		id                  : $('#trash-' + model_name + '-id').val(),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {
		if ('success' == data.status) {
			$('[data-' + model_name + ']').empty()
			$('#modal-delete-' + model_name).foundation('reveal', 'close');
		}
	}, "json");

	return false;
});
{% endif %}


{% if perms.catalog.change_updater %}
$("body").delegate("[data-do='switch-state-updater']", "click", function(){

	model_name = 'updater'

	$.post('/catalog/ajax/switch-state/' + model_name + '/', {
		id    : $(this).data('id'),
		state : $(this).prop('checked'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {
		if ('success' == data.status){
			return true;
		}
	}, "json");

	return true;
});
{% endif %}
