{% if perms.catalog.change_updater %}


// Открытие окна редактирования загрузчика (существующий)
$("body").delegate("[data-do*='open-edit-updater']", "click", function(){

	// Получаем информацию о загрузчике
	$.post("/catalog/ajax/get-updater/", {
		updater_id: $(this).data('id'),
		csrfmiddlewaretoken: '{{ csrf_token }}'
	},
	function(data) {
		if (null != data.status) {
			if ('success' == data.status){

				// Заполняем значение полей
				$('#edit-updater-id').val(data.updater_id);
				$('#edit-updater-name').val(data.updater_name);
				$('#edit-updater-alias').val(data.updater_alias);
				$('#edit-updater-login').val(data.updater_login);
				$('#edit-updater-password').val(data.updater_password);
				$('#edit-updater-state').prop('checked', data.updater_state);

				// Открываем окно
				$('#modal-edit-updater').foundation('reveal', 'open');

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


// Сохранение загрузчика
$("body").delegate("[data-do*='edit-updater-save']", "click", function(){

	// Отправляем запрос
	$.post("/catalog/ajax/save-updater/", {
		updater_id:          $('#edit-updater-id').val(),
		updater_name:        $('#edit-updater-name').val(),
		updater_alias:       $('#edit-updater-alias').val(),
		updater_login:       $('#edit-updater-login').val(),
		updater_password:    $('#edit-updater-password').val(),
		updater_state:       $('#edit-updater-state').prop('checked'),
		csrfmiddlewaretoken: '{{ csrf_token }}'
	},
	function(data) {
		if (null != data.status) {

			// Показываем сообщение
			var notification = new NotificationFx({
				wrapper: document.body,
				message: '<p>' + data.message + '</p>',
				layout:  'growl',
				effect:  'genie',
				type:    data.status,
				ttl:     3000,
				onClose: function() { return false; },
				onOpen:  function() { return false; }
			});
			notification.show();

			if ('success' == data.status){

				// Обновлем информацию на странице
				$("[data-updater-name*='" + $('#edit-updater-id').val() + "']").text($('#edit-updater-name').val());
				$("[data-updater-state*='" + $('#edit-updater-id').val() + "']").prop('checked', $('#edit-updater-state').prop('checked'));

				// Заполняем значение полей
				$('#edit-updater-id').val('0');
				$('#edit-updater-name').val('');
				$('#edit-updater-alias').val('');
				$('#edit-updater-login').val('');
				$('#edit-updater-password').val('');
				$('#edit-updater-state').prop('checked', false);

				// Закрываем окно
				$('#modal-edit-updater').foundation('reveal', 'close');
			}
		}
	}, "json");

	return false;
});


// Отмена редактирования загрузчика
$("body").delegate("[data-do*='edit-updater-cancel']", "click", function(){

	// Заполняем значение полей
	$('#edit-updater-id').val('0');
	$('#edit-updater-name').val('');
	$('#edit-updater-alias').val('');
	$('#edit-updater-login').val('');
	$('#edit-updater-password').val('');
	$('#edit-updater-state').prop('checked', false);

	// Закрываем окно
	$('#modal-edit-updater').foundation('reveal', 'close');

	return false;
});

{% endif %}

{% if perms.catalog.delete_updater %}


// Открытие модального окна удаления загрузчика
$("body").delegate("[data-do*='open-updater-trash']", "click", function(){

	// Заполняем значение полей
	$('#trash-updater-id').val($(this).data('id'));

	// Открываем окно
	$('#modal-trash-updater').foundation('reveal', 'open');

	return false;
});


// Удаление загрузчика
$("body").delegate("[data-do*='trash-updater']", "click", function(){

	// Отправляем запрос
	$.post("/catalog/ajax/trash-updater/", {
		updater_id:          $('#trash-updater-id').val(),
		csrfmiddlewaretoken: '{{ csrf_token }}'
	},
	function(data) {
		if (null != data.status) {

			// Показываем сообщение
			var notification = new NotificationFx({
				wrapper: document.body,
				message: '<p>' + data.message + '</p>',
				layout:  'growl',
				effect:  'genie',
				type:     data.status,
				ttl:      3000,
				onClose:  function() { return false; },
				onOpen:   function() { return false; }
			});
			notification.show();

			// Закрываем окно
			$('#modal-trash-updater').foundation('reveal', 'close');

			// Обновляем страницу
			setTimeout(function () {location.reload();}, 3000);
		}
	}, "json");

	return false;
});

{% endif %}

{% if perms.catalog.change_updater %}


// Смена статуса загрузчика
$("body").delegate("[data-do*='switch-updater-state']", "click", function(){

	// Отправляем запрос
	$.post("/catalog/ajax/switch-updater-state/", {
		updater_id:          $(this).data('id'),
		updater_state:       $(this).prop('checked'),
		csrfmiddlewaretoken: '{{ csrf_token }}'
	},
	function(data) {
		if (null != data.status) {

			// Показываем сообщение
			var notification = new NotificationFx({
				wrapper: document.body,
				message: '<p>' + data.message + '</p>',
				layout:  'growl',
				effect:  'genie',
				type:    data.status,
				ttl:     3000,
				onClose: function() { return false; },
				onOpen:  function() { return false; }
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
