{% if perms.catalog.add_parametertype %}


$("body").delegate("[data-do='open-new-parameter-type']", "click", function(){

	$('#modal-edit-parameter-type-header').text('Добавить тип данных параметров');
	$('#edit-parameter-type-id').val('0');
	$('#edit-parameter-type-name').val('');
	$('#edit-parameter-type-alias').val('');
	$('#edit-parameter-type-state').prop('checked', true);

	$('#modal-edit-parameter-type').foundation('reveal', 'open');
	return false;
});

{% endif %}

{% if perms.catalog.change_parametertype %}


$("body").delegate("[data-do='open-edit-parameter-type']", "click", function(){

	$.post("/catalog/ajax/get-parameter-type/", {
		id                  : $(this).data('id'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {
		if ('success' == data.status){

			$('#modal-edit-parameter-type-header').text('Редактировать тип данных параметров');
			$('#edit-parameter-type-id').val(data.parameter_type.id);
			$('#edit-parameter-type-name').val(data.parameter_type.name);
			$('#edit-parameter-type-alias').val(data.parameter_type.alias);
			$('#edit-parameter-type-state').prop('checked', data.parameter_type.state);

			$('#modal-edit-parameter-type').foundation('reveal', 'open');

		}
	}, "json");

	return false;
});


$("body").delegate("[data-do='edit-parameter-type-save']", "click", function(){

	$.post("/catalog/ajax/save-parameter-type/", {
		parameter_type_id        : $('#edit-parameter-type-id').val(),
		parameter_type_name      : $('#edit-parameter-type-name').val(),
		parameter_type_alias     : $('#edit-parameter-type-alias').val(),
		parameter_type_state     : $('#edit-parameter-type-state').prop('checked'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {

		if ('success' == data.status){

			o = data.parameter_type;

			$("[data-parameter-type-name='" + o.id + "']").text(o.name);
			$("[data-parameter-type-state='" + o.id + "']").prop('checked', o.state);

			$('#edit-parameter-type-id').val('0');
			$('#edit-parameter-type-name').val('');
			$('#edit-parameter-type-alias').val('');
			$('#edit-parameter-type-state').prop('checked', false);

			$('#modal-edit-parameter-type').foundation('reveal', 'close');
		}
	}, "json");
	return false;
});


$("body").delegate("[data-do='edit-parameter-type-cancel']", "click", function(){

	$('#edit-parameter-type-id').val('0');
	$('#edit-parameter-type-name').val('');
	$('#edit-parameter-type-alias').val('');
	$('#edit-parameter-type-data-type').val('');
	$('#edit-parameter-type-order').val('0');
	$('#edit-parameter-type-state').prop('checked', false);

	$('#modal-edit-parameter-type').foundation('reveal', 'close');

	return false;
});

{% endif %}

{% if perms.catalog.delete_parametertype %}


$("body").delegate("[data-do='open-parameter-type-trash']", "click", function(){

	$('#trash-parameter-type-id').val($(this).data('id'));

	$('#modal-trash-parameter-type').foundation('reveal', 'open');

	return false;
});


$("body").delegate("[data-do='trash-parameter-type']", "click", function(){

	// Отправляем запрос
	$.post("/catalog/ajax/trash-parameter-type/", {
		parameter_type_id   : $('#trash-parameter-type-id').val(),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {
		if (null != data.status) {

			// Показываем сообщение
			var notification = new NotificationFx({
				wrapper : document.body,
				message : '<p>' + data.message + '</p>',
				layout  : 'growl',
				effect  : 'genie',
				type    : data.status,
				ttl     : 3000,
				onClose : function() { return false; },
				onOpen  : function() { return false; }
			});
			notification.show();

			// Закрываем окно
			$('#modal-trash-parameter-type').foundation('reveal', 'close');

			// Обновляем страницу
			setTimeout(function () {location.reload();}, 3000);
		}
	}, "json");

	return false;
});

{% endif %}

{% if perms.catalog.change_parametertype %}


$("body").delegate("[data-do='switch-parameter-type-state']", "click", function(){
	$.post("/catalog/ajax/switch-parameter-type-state/", {
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
