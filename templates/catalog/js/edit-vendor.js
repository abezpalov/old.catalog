{% if perms.catalog.add_vendor %}

// Открытие окна редактирования производителя (новый)
$("body").delegate("[data-do='open-new-vendor']", "click", function(){

	// Заполняем значение полей
	$('#modal-edit-vendor-header').text('Добавить производителя');
	$('#edit-vendor-id').val('0');
	$('#edit-vendor-name').val('');
	$('#edit-vendor-alias').val('');
	$('#edit-vendor-description').val('');
	$('#edit-vendor-state').prop('checked', false);

	// Открываем модальное окно
	$('#modal-edit-vendor').foundation('reveal', 'open');
	return false;
});

{% endif %}

{% if perms.catalog.change_vendor %}


// Открытие окна редактирования производителя (существующий)
$("body").delegate("[data-do='open-edit-vendor']", "click", function(){

	// Получаем информацию о производителе
	$.post("/catalog/ajax/get-vendor/", {
		vendor_id:           $(this).data('id'),
		csrfmiddlewaretoken: '{{ csrf_token }}'
	},
	function(data) {
		if (null != data.status) {
			if ('success' == data.status){

				// Заполняем значение полей
				$('#modal-edit-vendor-header').text('Редактировать производителя');
				$('#edit-vendor-id').val(data.vendor_id);
				$('#edit-vendor-name').val(data.vendor_name);
				$('#edit-vendor-alias').val(data.vendor_alias);
				$('#edit-vendor-description').val(data.vendor_description);
				$('#edit-vendor-state').prop('checked', data.vendor_state);

				// Открываем окно
				$('#modal-edit-vendor').foundation('reveal', 'open');

			} else {

				// Показываем сообщение с ошибкой
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
			}
		}
	}, "json");

	return false;
});


// Сохранение производителя
$("body").delegate("[data-do='edit-vendor-save']", "click", function(){

	// Отправляем запрос
	$.post("/catalog/ajax/save-vendor/", {
		vendor_id:           $('#edit-vendor-id').val(),
		vendor_name:         $('#edit-vendor-name').val(),
		vendor_alias:        $('#edit-vendor-alias').val(),
		vendor_description:  $('#edit-vendor-description').val(),
		vendor_state:        $('#edit-vendor-state').prop('checked'),
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

			if ('success' == data.status){

				// Обновлем информацию на странице
				$("[data-vendor-name='" + $('#edit-vendor-id').val() + "']").text($('#edit-vendor-name').val());
				$("[data-vendor-state='" + $('#edit-vendor-id').val() + "']").prop('checked', $('#edit-vendor-state').prop('checked'));

				// Заполняем значение полей
				$('#edit-vendor-id').val('0');
				$('#edit-vendor-name').val('');
				$('#edit-vendor-alias').val('');
				$('#edit-vendor-description').val('');
				$('#edit-vendor-state').prop('checked', false);

				// Закрываем окно
				$('#modal-edit-vendor').foundation('reveal', 'close');
			}
		}
	}, "json");

	return false;
});


// Отмена редактирования производителя
$("body").delegate("[data-do='edit-vendor-cancel']", "click", function(){

	// Заполняем значение полей
	$('#edit-vendor-id').val('0');
	$('#edit-vendor-name').val('');
	$('#edit-vendor-alias').val('');
	$('#edit-vendor-description').val('');
	$('#edit-vendor-state').prop('checked', false);

	// Закрываем окно
	$('#modal-edit-vendor').foundation('reveal', 'close');

	return false;
});

{% endif %}

{% if perms.catalog.delete_vendor %}


// Открытие модального окна удаления производителя
$("body").delegate("[data-do='open-vendor-trash']", "click", function(){

	// Заполняем значение полей
	$('#trash-vendor-id').val($(this).data('id'));

	// Открываем окно
	$('#modal-trash-vendor').foundation('reveal', 'open');

	return false;
});


// Удаление производителя
$("body").delegate("[data-do='trash-vendor']", "click", function(){

	// Отправляем запрос
	$.post("/catalog/ajax/trash-vendor/", {
		vendor_id:           $('#trash-vendor-id').val(),
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
			$('#modal-trash-vendor').foundation('reveal', 'close');

			// Обновляем страницу
			setTimeout(function () {location.reload();}, 3000);
		}
	}, "json");

	return false;
});

{% endif %}

{% if perms.catalog.change_vendor %}


// Смена статуса производителя
$("body").delegate("[data-do='switch-vendor-state']", "click", function(){

	// Отправляем запрос
	$.post("/catalog/ajax/switch-vendor-state/", {
		vendor_id:           $(this).data('id'),
		vendor_state:        $(this).prop('checked'),
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
