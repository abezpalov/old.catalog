{% if perms.catalog.change_distributors %}


// Открытие окна редактирования поставщика (существующий)
$("body").delegate("[data-do*='open-edit-distributor']", "click", function(){

	// Получаем информацию о поставщике
	$.post("/catalog/ajax/get-distributor/", {
		distributor_id: $(this).data('id'),
		csrfmiddlewaretoken: '{{ csrf_token }}'
	},
	function(data) {
		if (null != data.status) {
			if ('success' == data.status){

				// Заполняем значение полей
				$('#edit-distributor-id').val(data.distributor_id);
				$('#edit-distributor-name').val(data.distributor_name);
				$('#edit-distributor-alias').val(data.distributor_alias);
				$('#edit-distributor-description').val(data.distributor_description);
				$('#edit-distributor-state').prop('checked', data.distributor_state);

				// Открываем окно
				$('#modal-edit-distributor').foundation('reveal', 'open');

			} else {

				// Показываем сообщение с ошибкой
				var notification = new NotificationFx({
					wrapper : document.body,
					message : '<p>' + data.message + '</p>',
					layout : 'growl',
					effect : 'genie',
					type : data.status,
					ttl : 3000,
					onClose : function() { return false; },
					onOpen : function() { return false; }
				});
				notification.show();
			}
		}
	}, "json");

	return false;
});


// Сохранение поставщика
$("body").delegate("[data-do*='edit-distributor-save']", "click", function(){

	// Получаем информацию о поставщике
	$.post("/catalog/ajax/save-distributor/", {
		distributor_id:          $('#edit-distributor-id').val(),
		distributor_name:        $('#edit-distributor-name').val(),
		distributor_alias:       $('#edit-distributor-alias').val(),
		distributor_description: $('#edit-distributor-description').val(),
		distributor_state:       $('#edit-distributor-state').prop('checked'),
		csrfmiddlewaretoken:     '{{ csrf_token }}'
	},
	function(data) {
		if (null != data.status) {

			// Показываем сообщение
			var notification = new NotificationFx({
				wrapper : document.body,
				message : '<p>' + data.message + '</p>',
				layout : 'growl',
				effect : 'genie',
				type : data.status,
				ttl : 3000,
				onClose : function() { return false; },
				onOpen : function() { return false; }
			});
			notification.show();

			if ('success' == data.status){

				// Обновлем информацию на странице
				$("[data-distributor-name*='" + $('#edit-distributor-id').val() + "']").text($('#edit-distributor-name').val());
				$("[data-distributor-state*='" + $('#edit-distributor-id').val() + "']").prop('checked', $('#edit-distributor-state').prop('checked'));

				// Заполняем значение полей
				$('#edit-distributor-id').val('0');
				$('#edit-distributor-name').val('');
				$('#edit-distributor-alias').val('');
				$('#edit-distributor-state').prop('checked', false);

				// Закрываем окно
				$('#modal-edit-distributor').foundation('reveal', 'close');
			}
		}
	}, "json");

	return false;
});


// Отмена редактирования поставщика
$("body").delegate("[data-do*='edit-distributor-cancel']", "click", function(){

	// Заполняем значение полей
	$('#edit-distributor-id').val('0');
	$('#edit-distributor-name').val('');
	$('#edit-distributor-alias').val('');
	$('#edit-distributor-state').prop('checked', false);

	// Закрываем окно
	$('#modal-edit-distributor').foundation('reveal', 'close');

	return false;
});

{% endif %}

{% if perms.catalog.delete_distributor %}


// Открытие модального окна удаления поставщика
$("body").delegate("[data-do*='open-distributor-trash']", "click", function(){

	// Заполняем значение полей
	$('#trash-distributor-id').val($(this).data('id'));

	// Открываем окно
	$('#modal-trash-distributor').foundation('reveal', 'open');

	return false;
});


// Удаление поставщика
$("body").delegate("[data-do*='trash-distributor']", "click", function(){

	// Отправляем запрос
	$.post("/catalog/ajax/trash-distributor/", {
		distributor_id: $('#trash-distributor-id').val(),
		csrfmiddlewaretoken: '{{ csrf_token }}'
	},
	function(data) {
		if (null != data.status) {

			// Показываем сообщение
			var notification = new NotificationFx({
				wrapper : document.body,
				message : '<p>' + data.message + '</p>',
				layout : 'growl',
				effect : 'genie',
				type : data.status,
				ttl : 3000,
				onClose : function() { return false; },
				onOpen : function() { return false; }
			});
			notification.show();

			// Закрываем окно
			$('#modal-trash-distributor').foundation('reveal', 'close');

			// Обновляем страницу
			setTimeout(function () {location.reload();}, 3000);
		}
	}, "json");

	return false;
});

{% endif %}

{% if perms.catalog.change_distributor %}


// Смена статуса поставщика
$("body").delegate("[data-do*='switch-distributor-state']", "click", function(){

	// Отправляем запрос
	$.post("/catalog/ajax/switch-distributor-state/", {
		distributor_id:      $(this).data('id'),
		distributor_state:   $(this).prop('checked'),
		csrfmiddlewaretoken: '{{ csrf_token }}'
	},
	function(data) {
		if (null != data.status) {

			// Показываем сообщение
			var notification = new NotificationFx({
				wrapper : document.body,
				message : '<p>' + data.message + '</p>',
				layout : 'growl',
				effect : 'genie',
				type : data.status,
				ttl : 3000,
				onClose : function() { return false; },
				onOpen : function() { return false; }
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
