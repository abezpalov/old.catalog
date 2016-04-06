{% if perms.catalog.add_parameter %}


$("body").delegate("[data-do='open-new-parameter']", "click", function(){

	// Заполняем значение полей
	$('#modal-edit-parameter-header').text('Добавить параметр');
	$('#edit-parameter-id').val('0');
	$('#edit-parameter-name').val('');
	$('#edit-parameter-alias').val('');
	$('#edit-parameter-parameter-type').val('');
	$('#edit-parameter-order').val('0');
	$('#edit-parameter-state').prop('checked', false);

	// Открываем модальное окно
	$('#modal-edit-parameter').foundation('reveal', 'open');
	return false;
});

{% endif %}

{% if perms.catalog.change_parameter %}


$("body").delegate("[data-do='open-edit-parameter']", "click", function(){

	// Получаем информацию о производителе
	$.post("/catalog/ajax/get-parameter/", {
		parameter_id        : $(this).data('id'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {
		if (null != data.status) {
			if ('success' == data.status){

				// Заполняем значение полей
				$('#modal-edit-parameter-header').text('Редактировать параметр');
				$('#edit-parameter-id').val(data.parameter.id);
				$('#edit-parameter-name').val(data.parameter.name);
				$('#edit-parameter-alias').val(data.parameter.alias);
				$('#edit-parameter-parameter-type').val(data.parameter.parameter_type.id);
				$('#edit-parameter-order').val(data.parameter.order);
				$('#edit-parameter-state').prop('checked', data.parameter.state);

				// Открываем окно
				$('#modal-edit-parameter').foundation('reveal', 'open');

			} else {

				// Показываем сообщение с ошибкой
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
			}
		}
	}, "json");

	return false;
});


$("body").delegate("[data-do='edit-parameter-save']", "click", function(){

	// Отправляем запрос
	$.post("/catalog/ajax/save-parameter/", {
		parameter_id                : $('#edit-parameter-id').val(),
		parameter_name              : $('#edit-parameter-name').val(),
		parameter_alias             : $('#edit-parameter-alias').val(),
		parameter_parameter_type_id : $('#edit-parameter-parameter-type').val(),
		parameter_order             : $('#edit-parameter-order').val(),
		parameter_state             : $('#edit-parameter-state').prop('checked'),
		csrfmiddlewaretoken         : '{{ csrf_token }}'
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

			if ('success' == data.status){

				// Обновлем информацию на странице
				$("[data-parameter-name='" + $('#edit-parameter-id').val() + "']").text($('#edit-parameter-name').val());
				$("[data-parameter-state='" + $('#edit-parameter-id').val() + "']").prop('checked', $('#edit-parameter-state').prop('checked'));

				// Заполняем значение полей
				$('#edit-parameter-id').val('0');
				$('#edit-parameter-name').val('');
				$('#edit-parameter-alias').val('');
				$('#edit-parameter-parameter-type').val('');
				$('#edit-parameter-order').val('0');
				$('#edit-parameter-state').prop('checked', false);

				// Закрываем окно
				$('#modal-edit-parameter').foundation('reveal', 'close');
			}
		}
	}, "json");

	return false;
});


$("body").delegate("[data-do='edit-parameter-cancel']", "click", function(){

	// Заполняем значение полей
	$('#edit-parameter-id').val('0');
	$('#edit-parameter-name').val('');
	$('#edit-parameter-alias').val('');
	$('#edit-parameter-data-type').val('');
	$('#edit-parameter-order').val('0');
	$('#edit-parameter-state').prop('checked', false);

	// Закрываем окно
	$('#modal-edit-parameter').foundation('reveal', 'close');

	return false;
});

{% endif %}

{% if perms.catalog.delete_parameter %}


$("body").delegate("[data-do='open-parameter-trash']", "click", function(){

	// Заполняем значение полей
	$('#trash-parameter-id').val($(this).data('id'));

	// Открываем окно
	$('#modal-trash-parameter').foundation('reveal', 'open');

	return false;
});


$("body").delegate("[data-do='trash-parameter']", "click", function(){

	// Отправляем запрос
	$.post("/catalog/ajax/trash-parameter/", {
		parameter_id        : $('#trash-parameter-id').val(),
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
			$('#modal-trash-parameter').foundation('reveal', 'close');

			// Обновляем страницу
			setTimeout(function () {location.reload();}, 3000);
		}
	}, "json");

	return false;
});

{% endif %}

{% if perms.catalog.change_parameter %}


$("body").delegate("[data-do='switch-parameter-state']", "click", function(){

	// Отправляем запрос
	$.post("/catalog/ajax/switch-parameter-state/", {
		parameter_id        : $(this).data('id'),
		parameter_state     : $(this).prop('checked'),
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

			// Проверем успешность запроса
			if ('success' != data.status){
				setTimeout(function () {location.reload();}, 3000);
			}
		}
	}, "json");

	return true;
});

{% endif %}
