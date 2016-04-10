{% if perms.catalog.add_parametervalue %}


$("body").delegate("[data-do='open-new-parameter-value']", "click", function(){

	$('#modal-edit-parameter-value-header').text('Добавить значение параметра');
	$('#edit-parameter-value-id').val('0');
	$('#edit-parameter-value-parameter').val('');
	$('#edit-parameter-value-value-text').val('');
	$('#edit-parameter-value-order').val('0');
	$('#edit-parameter-value-state').prop('checked', true);

	$('#modal-edit-parameter-value').foundation('reveal', 'open');
	return false;
});

{% endif %}

{% if perms.catalog.change_parametervalue %}


$("body").delegate("[data-do='open-edit-parameter-value']", "click", function(){

	$.post("/catalog/ajax/get-parameter-value/", {
		id                  : $(this).data('id'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {
		if (null != data.status) {
			if ('success' == data.status){

				$('#modal-edit-parameter-value-header').text('Редактировать значение параметра');
				$('#edit-parameter-value-id').val(data.parameter_value.id);
				$('#edit-parameter-value-parameter').val(data.parameter_value.parameter.id);
				$('#edit-parameter-value-value_text').val(data.parameter_value.value_text);
				$('#edit-parameter-value-order').val(data.parameter_value.order);
				$('#edit-parameter-value-state').prop('checked', data.parameter_value.state);

				$('#modal-edit-parameter-value').foundation('reveal', 'open');
			}
		}
	}, "json");

	return false;
});


$("body").delegate("[data-do='edit-parameter-value-save']", "click", function(){

	$.post("/catalog/ajax/save-parameter-value/", {
		parameter_value_id           : $('#edit-parameter-value-id').val(),
		parameter_value_parameter_id : $('#edit-parameter-value-parameter').val(),
		parameter_value_value_text   : $('#edit-parameter-value-value-text').val(),
		parameter_value_order        : $('#edit-parameter-value-order').val(),
		parameter_value_state        : $('#edit-parameter-value-state').prop('checked'),
		csrfmiddlewaretoken          : '{{ csrf_token }}'
	},
	function(data) {
		if ('success' == data.status){

			o = data.parameter_value

			$("[data-parameter-value-value-search='" + o.id + "']").text(o.value_search);
			$("[data-parameter-state='" + o.id + "']").prop('checked', o.state);
			$("[data-parameter-value-parameter-name='" + o.id + "']").text(o.parameter.name);

			$('#edit-parameter-value-id').val('0');
			$('#edit-parameter-value-parameter').val('0');
			$('#edit-parameter-value-value-text').val('');
			$('#edit-parameter-value-order').val('0');
			$('#edit-parameter-value-state').prop('checked', false);

			$('#modal-edit-parameter-value').foundation('reveal', 'close');
		}
	}, "json");

	return false;
});


$("body").delegate("[data-do='edit-parameter-value-cancel']", "click", function(){

	$('#edit-parameter-value-id').val('0');
	$('#edit-parameter-value-parameter').val('0');
	$('#edit-parameter-value-value-text').val('');
	$('#edit-parameter-value-order').val('0');
	$('#edit-parameter-value-state').prop('checked', false);

	$('#modal-edit-value-parameter').foundation('reveal', 'close');

	return false;
});

{% endif %}

{% if perms.catalog.delete_parametervalue %}


$("body").delegate("[data-do='open-parameter-value-trash']", "click", function(){

	$('#trash-parameter-value-id').val($(this).data('id'));

	$('#modal-trash-parameter-value').foundation('reveal', 'open');

	return false;
});


$("body").delegate("[data-do='trash-parameter-value']", "click", function(){
	$.post("/catalog/ajax/trash-parameter-value/", {
		id                  : $('#trash-parameter-value-id').val(),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {
		if ('success' != data.status) {

			$("[data-parameter-value]").empty()

			$('#modal-trash-parameter-value').foundation('reveal', 'close');

		}
	}, "json");
	return false;
});

{% endif %}

{% if perms.catalog.change_parameter %}

$("body").delegate("[data-do='switch-parameter-value-state']", "click", function(){
	$.post("/catalog/ajax/switch-parameter-value-state/", {
		id                  : $(this).data('id'),
		state               : $(this).prop('checked'),
		csrfmiddlewaretoken : '{{ csrf_token }}'},
	function(data) {
		if ('success' != data.status) {
			return true;
		} else {
			return false;
		}
	}, "json");
});

{% endif %}
