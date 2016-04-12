{% if perms.catalog.change_distributor %}
$("body").delegate("[data-do='open-edit-distributor']", "click", function(){

	model_name = 'distributor'

	$.post('/catalog/ajax/get/' + model_name + '/', {
		id : $(this).data('id'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {
		if ('success' == data.status){

			$('#modal-edit-' + model_name + '-header').text('Редактировать поставщика');
			$('#edit-' + model_name + '-id').val(data[model_name]['id']);
			$('#edit-' + model_name + '-name').val(data[model_name]['name']);
			$('#edit-' + model_name + '-alias').val(data[model_name]['alias']);
			$('#edit-' + model_name + '-description').val(data[model_name]['description']);
			$('#edit-' + model_name + '-state').prop('checked', data[model_name]['state']);

			$('#modal-edit-' + model_name).foundation('reveal', 'open');
		}
	}, "json");
	return false;
});
{% endif %}


{% if perms.catalog.change_distributor %}
$("body").delegate("[data-do='edit-distributor-save']", "click", function(){

	model_name = 'distributor'

	$.post("/catalog/ajax/save-distributor/", {
		id          : $('#edit-' + model_name + '-id').val(),
		name        : $('#edit-' + model_name + '-name').val(),
		alias       : $('#edit-' + model_name + '-alias').val(),
		description : $('#edit-' + model_name + '-description').val(),
		state       : $('#edit-' + model_name + '-state').prop('checked'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {

		if ('success' == data.status){

			$("[data-" + model_name + "-name='" + $('#edit-' + model_name + '-id').val() + "']").text(data[model_name]['name']);
			$("[data-" + model_name + "-state='" + $('#edit-' + model_name + '-id').val() + "']").prop('checked', data[model_name]['state']);

			$('#edit-' + model_name + '-id').val('0');
			$('#edit-' + model_name + '-name').val('');
			$('#edit-' + model_name + '-alias').val('');
			$('#edit-' + model_name + '-description').val('');
			$('#edit-' + model_name + '-state').prop('checked', false);

			$('#modal-edit-' + model_name).foundation('reveal', 'close');
		}
	}, "json");

	return false;
});
{% endif %}


{% if perms.catalog.change_distributor %}
$("body").delegate("[data-do='edit-distributor-cancel']", "click", function(){

	model_name = 'distributor'

	$('#edit-' + model_name + '-id').val('0');
	$('#edit-' + model_name + '-name').val('');
	$('#edit-' + model_name + '-alias').val('');
	$('#edit-' + model_name + '-description').val('');
	$('#edit-' + model_name + '-state').prop('checked', false);

	$('#modal-edit-' + model_name).foundation('reveal', 'close');

	return false;
});
{% endif %}


{% if perms.catalog.delete_distributor %}
$("body").delegate("[data-do='open-delete-distributor']", "click", function(){

	model_name = 'distributor'

	$('#delete-' + model_name + '-id').val($(this).data('id'));

	$('#modal-delete-' + model_name).foundation('reveal', 'open');

	return false;
});
{% endif %}


{% if perms.catalog.delete_distributor %}
$("body").delegate("[data-do='delete-distributor']", "click", function(){

	model_name = 'distributor'

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


{% if perms.catalog.change_distributor %}
$("body").delegate("[data-do='switch-state-distributor']", "click", function(){

	model_name = 'distributor'

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
