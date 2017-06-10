{% if perms.catalog.change_updater %}
$("body").delegate("[data-do='open-edit-updater']", "click", function(){

	model = 'updater';

	$.post('/catalog/ajax/get/' + model + '/', {
		id : $(this).data(model + '-id'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {
		if ('success' == data.status){

			$('#modal-edit-' + model + '-header').text('Редактировать загрузчик');
			$('#edit-' + model + '-id').val(data[model]['id']);
			$('#edit-' + model + '-name').val(data[model]['name']);
			$('#edit-' + model + '-alias').val(data[model]['alias']);
			$('#edit-' + model + '-login').val(data[model]['login']);
			$('#edit-' + model + '-password').val(data[model]['password']);
			$('#edit-' + model + '-state').prop('checked', data[model]['state']);

			$('#modal-edit-' + model).foundation('open');
		}
	}, "json");
	return false;
});
{% endif %}


{% if perms.catalog.change_updater %}
$("body").delegate("[data-do='edit-updater-save']", "click", function(){

	model = 'updater';

	$.post('/catalog/ajax/save/' + model + '/', {
		id       : $('#edit-' + model + '-id').val(),
		name     : $('#edit-' + model + '-name').val(),
		alias    : $('#edit-' + model + '-alias').val(),
		login    : $('#edit-' + model + '-login').val(),
		password : $('#edit-' + model + '-password').val(),
		state    : $('#edit-' + model + '-state').prop('checked'),
		csrfmiddlewaretoken: '{{ csrf_token }}'
	},
	function(data) {
		if ('success' == data.status){

			$("[data-" + model + "-name='" + $('#edit-' + model + '-id').val() + "']").text(data[model]['name']);
			$("[data-" + model + "-state='" + $('#edit-' + model + '-id').val() + "']").prop('checked', data[model]['state']);

			$('#edit-' + model + '-id').val('0');
			$('#edit-' + model + '-name').val('');
			$('#edit-' + model + '-alias').val('');
			$('#edit-' + model + '-login').val('');
			$('#edit-' + model + '-password').val('');
			$('#edit-' + model + '-state').prop('checked', false);

			$('#modal-edit-' + model).foundation('close');
		}
	}, "json");
	return false;
});
{% endif %}


{% if perms.catalog.change_updater %}
$("body").delegate("[data-do='edit-updater-cancel']", "click", function(){

	model = 'updater';

	$('#edit-' + model + '-id').val('0');
	$('#edit-' + model + '-name').val('');
	$('#edit-' + model + '-alias').val('');
	$('#edit-' + model + '-login').val('');
	$('#edit-' + model + '-password').val('');
	$('#edit-' + model + '-state').prop('checked', false);

	$('#modal-edit-' + model).foundation('close');

	return false;
});
{% endif %}


{% if perms.catalog.delete_updater %}
$("body").delegate("[data-do='open-delete-updater']", "click", function(){

	model = 'updater'

	$('#delete-' + model + '-id').val($(this).data('id'));

	$('#modal-delete-' + model).foundation('open');

	return false;
});
{% endif %}


{% if perms.catalog.delete_updater %}
$("body").delegate("[data-do='trash-updater']", "click", function(){

	model = 'updater';

	$.post('/catalog/ajax/delete/' + model + '/', {
		id                  : $('#trash-' + model + '-id').val(),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {
		if ('success' == data.status) {
			$('[data-' + model + ']').empty()
			$('#modal-delete-' + model).foundation('close');
		}
	}, "json");

	return false;
});
{% endif %}


{% if perms.catalog.change_updater %}
$("body").delegate("[data-do='switch-state-updater']", "click", function(){

	model = 'updater';

	$.post('/catalog/ajax/switch-state/' + model + '/', {
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
