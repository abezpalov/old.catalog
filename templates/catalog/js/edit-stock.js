{% if perms.catalog.change_stock %}


// Открытие окна редактирования склада (существующий)
$("body").delegate("[data-do*='open-edit-stock']", "click", function(){

	// Получаем информацию о складе
	$.post("/catalog/ajax/get-stock/", {
		stock_id: $(this).data('id'),
		csrfmiddlewaretoken: '{{ csrf_token }}'
	},
	function(data) {
		if (null != data.status) {
			if ('success' == data.status){

				// Заполняем значение полей
				$('#edit-stock-id').val(data.stock_id);
				$('#edit-stock-name').val(data.stock_name);
				$('#edit-stock-alias').val(data.stock_alias);
				$('#edit-stock-delivery-time-min').val(data.stock_delivery_time_min);
				$('#edit-stock-delivery-time-max').val(data.stock_delivery_time_max);
				$('#edit-stock-state').prop('checked', data.stock_state);

				// Открываем окно
				$('#modal-edit-stock').foundation('reveal', 'open');

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


// Сохранение склада
$("body").delegate("[data-do*='edit-stock-save']", "click", function(){

	// Отправляем запрос
	$.post("/catalog/ajax/save-stock/", {
		stock_id:                $('#edit-stock-id').val(),
		stock_name:              $('#edit-stock-name').val(),
		stock_alias:             $('#edit-stock-alias').val(),
		stock_delivery_time_min: $('#edit-stock-delivery-time-min').val(),
		stock_delivery_time_max: $('#edit-stock-delivery-time-max').val(),
		stock_state:             $('#edit-stock-state').prop('checked'),
		csrfmiddlewaretoken:     '{{ csrf_token }}'
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
				$("[data-stock-name*='" + $('#edit-stock-id').val() + "']").text($('#edit-stock-name').val());
				$("[data-stock-delivery-time-min*='" + $('#edit-stock-id').val() + "']").text($('#edit-stock-delivery-time-min').val());
				$("[data-stock-delivery-time-max*='" + $('#edit-stock-id').val() + "']").text($('#edit-stock-delivery-time-max').val());
				$("[data-stock-state*='" + $('#edit-stock-id').val() + "']").prop('checked', $('#edit-stock-state').prop('checked'));

				// Заполняем значение полей
				$('#edit-stock-id').val('0');
				$('#edit-stock-name').val('');
				$('#edit-stock-alias').val('');
				$('#edit-stock-delivery-time-min').val('');
				$('#edit-stock-delivery-time-max').val('');
				$('#edit-stock-state').prop('checked', false);

				// Закрываем окно
				$('#modal-edit-stock').foundation('reveal', 'close');
			}
		}
	}, "json");

	return false;
});


// Отмена редактирования склада
$("body").delegate("[data-do*='edit-stock-cancel']", "click", function(){

	// Заполняем значение полей
	$('#edit-stock-id').val('0');
	$('#edit-stock-name').val('');
	$('#edit-stock-alias').val('');
	$('#edit-stock-delivery-time-min').val('');
	$('#edit-stock-delivery-time-max').val('');
	$('#edit-stock-state').prop('checked', false);

	// Закрываем окно
	$('#modal-edit-stock').foundation('reveal', 'close');

	return false;
});

{% endif %}

{% if perms.catalog.delete_stock %}


// Открытие модального окна удаления склада
$("body").delegate("[data-do*='open-stock-trash']", "click", function(){

	// Заполняем значение полей
	$('#trash-stock-id').val($(this).data('id'));

	// Открываем окно
	$('#modal-trash-stock').foundation('reveal', 'open');

	return false;
});


// Удаление склада
$("body").delegate("[data-do*='trash-stock']", "click", function(){

	// Отправляем запрос
	$.post("/catalog/ajax/trash-stock/", {
		stock_id:            $('#trash-stock-id').val(),
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
			$('#modal-trash-stock').foundation('reveal', 'close');

			// Обновляем страницу
			setTimeout(function () {location.reload();}, 3000);
		}
	}, "json");

	return false;
});

{% endif %}

{% if perms.catalog.change_stock %}


// Смена статуса склада
$("body").delegate("[data-do*='switch-stock-state']", "click", function(){

	// Отправляем запрос
	$.post("/catalog/ajax/switch-stock-state/", {
		stock_id:            $(this).data('id'),
		stock_state:         $(this).prop('checked'),
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
