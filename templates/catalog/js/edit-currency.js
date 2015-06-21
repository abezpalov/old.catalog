{% if perms.catalog.add_currency %}

// Открытие окна редактирования валюты (новая)
$("body").delegate("[data-do='open-new-currency']", "click", function(){

	// Заполняем значение полей
	$('#modal-edit-currency-header').text('Добавить валюту');
	$('#edit-currency-id').val('0');
	$('#edit-currency-name').val('');
	$('#edit-currency-fulle-name').val('');
	$('#edit-currency-alias').val('');
	$('#edit-currency-rate').val('0.0');
	$('#edit-currency-quantity').val('0');
	$('#edit-currency-state').prop('checked', false);

	// Открываем модальное окно
	$('#modal-edit-currency').foundation('reveal', 'open');
	return false;
});

{% endif %}

{% if perms.catalog.change_currency %}


// Открытие окна редактирования валюты (существующая)
$("body").delegate("[data-do='open-edit-currency']", "click", function(){

	// Получаем информацию о категории
	$.post("/catalog/ajax/get-currency/", {
		currency_id:         $(this).data('id'),
		csrfmiddlewaretoken: '{{ csrf_token }}'
	},
	function(data) {
		if (null != data.status) {
			if ('success' == data.status){

				// Заполняем значение полей
				$('#modal-edit-currency-header').text('Редактировать валюту');
				$('#edit-currency-id').val(data.currency['id']);
				$('#edit-currency-name').val(data.currency['name']);
				$('#edit-currency-full-name').val(data.currency['full_name']);
				$('#edit-currency-alias').val(data.currency['alias']);
				$('#edit-currency-rate').val(data.currency['rate']);
				$('#edit-currency-quantity').val(data.currency['quantity']);
				$('#edit-currency-state').prop('checked', data.currency['state']);

				// Открываем окно
				$('#modal-edit-currency').foundation('reveal', 'open');

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


// Сохранение
$("body").delegate("[data-do='edit-currency-save']", "click", function(){

	// Отправляем запрос
	$.post("/catalog/ajax/save-currency/", {
		currency_id:           $('#edit-currency-id').val(),
		currency_name:         $('#edit-currency-name').val(),
		currency_full_name:    $('#edit-currency-full-name').val(),
		currency_alias:        $('#edit-currency-alias').val(),
		currency_rate:         $('#edit-currency-rate').val(),
		currency_quantity:     $('#edit-currency-quantity').val(),
		currency_state:        $('#edit-currency-state').prop('checked'),
		csrfmiddlewaretoken:  '{{ csrf_token }}'
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
				$("[data-currency-full-name='" + $('#edit-currency-id').val() + "']").text($('#edit-currency-full-name').val());
				$("[data-currency-alias='" + $('#edit-currency-id').val() + "']").text($('#edit-currency-alias').val());
				$("[data-currency-state='" + $('#edit-currency-id').val() + "']").prop('checked', $('#edit-currency-state').prop('checked'));

				// Заполняем значение полей
				$('#edit-currency-id').val('0');
				$('#edit-currency-name').val('');
				$('#edit-currency-fulle-name').val('');
				$('#edit-currency-alias').val('');
				$('#edit-currency-rate').val('0.0');
				$('#edit-currency-quantity').val('0.0');
				$('#edit-currency-state').prop('checked', false);

				// Закрываем окно
				$('#modal-edit-currency').foundation('reveal', 'close');
			}
		}
	}, "json");

	return false;
});


// Отмена редактирования категории
$("body").delegate("[data-do='edit-currency-cancel']", "click", function(){

	// Заполняем значение полей
	$('#edit-currency-id').val('0');
	$('#edit-currency-name').val('');
	$('#edit-currency-fulle-name').val('');
	$('#edit-currency-alias').val('');
	$('#edit-currency-rate').val('0.0');
	$('#edit-currency-quantity').val('0');
	$('#edit-currency-state').prop('checked', false);

	// Закрываем окно
	$('#modal-edit-currency').foundation('reveal', 'close');

	return false;
});

{% endif %}

{% if perms.catalog.delete_currency %}


// Открытие модального окна удаления категории
$("body").delegate("[data-do='open-delete-currency']", "click", function(){

	// Получаем информацию о категории
	$.post("/catalog/ajax/get-currency/", {
		currency_id:         $(this).data('id'),
		csrfmiddlewaretoken: '{{ csrf_token }}'
	},
	function(data) {
		if (null != data.status) {
			if ('success' == data.status){

				// Заполняем значение полей
				$('#delete-currency-id').val(data.currency['id']);
				$('#delete-currency-full-name').text(data.currency['full_name'])

				// Открываем окно
				$('#modal-delete-currency').foundation('reveal', 'open');

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


// Удаление производителя
$("body").delegate("[data-do='delete-currency-apply']", "click", function(){

	// Отправляем запрос
	$.post("/catalog/ajax/delete-currency/", {
		currency_id:         $('#delete-currency-id').val(),
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
			$('#modal-delete-currency').foundation('reveal', 'close');

			// Обновляем страницу
			setTimeout(function () {location.reload();}, 3000);
		}
	}, "json");

	return false;
});

{% endif %}

{% if perms.catalog.change_currency %}


// Смена статуса производителя
$("body").delegate("[data-do='switch-currency-state']", "click", function(){

	// Отправляем запрос
	$.post("/catalog/ajax/switch-currency-state/", {
		currency_id:         $(this).data('id'),
		currency_state:      $(this).prop('checked'),
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
