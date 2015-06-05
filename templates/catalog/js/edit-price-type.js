{% if perms.catalog.change_pricetype %}


// Открытие окна редактирования типа цены (существующий)
$("body").delegate("[data-do*='open-edit-price-type']", "click", function(){

	// Получаем информацию о типе цены
	$.post("/catalog/ajax/get-price-type/", {
		price_type_id: $(this).data('id'),
		csrfmiddlewaretoken: '{{ csrf_token }}'
	},
	function(data) {
		if (null != data.status) {
			if ('success' == data.status){

				// Заполняем значение полей
				$('#edit-price-type-id').val(data.price_type_id);
				$('#edit-price-type-name').val(data.price_type_name);
				$('#edit-price-type-alias').val(data.price_type_alias);
				$('#edit-price-type-multiplier').val(data.price_type_multiplier);
				$('#edit-price-type-state').prop('checked', data.price_type_state);

				// Открываем окно
				$('#modal-edit-price-type').foundation('reveal', 'open');

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


// Сохранение типа цены
$("body").delegate("[data-do*='edit-price-type-save']", "click", function(){

	// Получаем информацию о типе цены
	$.post("/catalog/ajax/save-price-type/", {
		price_type_id:         $('#edit-price-type-id').val(),
		price_type_name:       $('#edit-price-type-name').val(),
		price_type_alias:      $('#edit-price-type-alias').val(),
		price_type_multiplier: $('#edit-price-type-multiplier').val(),
		price_type_state:      $('#edit-price-type-state').prop('checked'),
		csrfmiddlewaretoken:   '{{ csrf_token }}'
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
				$("[data-price-type-name*='" + $('#edit-price-type-id').val() + "']").text($('#edit-price-type-name').val());
				$("[data-price-type-state*='" + $('#edit-price-type-id').val() + "']").prop('checked', $('#edit-price-type-state').prop('checked'));
				$("[data-price-type-multiplier*='" + $('#edit-price-type-id').val() + "']").text($('#edit-price-type-multiplier').val());

				// Заполняем значение полей
				$('#edit-price-type-id').val('0');
				$('#edit-price-type-name').val('');
				$('#edit-price-type-alias').val('');
				$('#edit-price-type-multiplier').val('1.0');
				$('#edit-price-type-state').prop('checked', false);

				// Закрываем окно
				$('#modal-edit-price-type').foundation('reveal', 'close');
			}
		}
	}, "json");

	return false;
});


// Отмена редактирования типа цены
$("body").delegate("[data-do*='edit-price-type-cancel']", "click", function(){

	// Заполняем значение полей
	$('#edit-price-type-id').val('0');
	$('#edit-price-type-name').val('');
	$('#edit-price-type-alias').val('');
	$('#edit-price-type-multiplier').val('1.0');
	$('#edit-price-type-state').prop('checked', false);

	// Закрываем окно
	$('#modal-edit-price-type').foundation('reveal', 'close');

	return false;
});

{% endif %}

{% if perms.catalog.delete_pricetype %}


// Открытие модального окна удаления типа цены
$("body").delegate("[data-do*='open-price-type-trash']", "click", function(){

	// Заполняем значение полей
	$('#trash-price-type-id').val($(this).data('id'));

	// Открываем окно
	$('#modal-trash-price-type').foundation('reveal', 'open');

	return false;
});


// Удаление типа цены
$("body").delegate("[data-do*='trash-price-type']", "click", function(){

	// Отправляем запрос
	$.post("/catalog/ajax/trash-price-type/", {
		price_type_id: $('#trash-price-type-id').val(),
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

{% if perms.catalog.change_pricetype %}


// Смена статуса типа цены
$("body").delegate("[data-do*='switch-price-type-state']", "click", function(){

	// Отправляем запрос
	$.post("/catalog/ajax/switch-price-type-state/", {
		price_type_id:      $(this).data('id'),
		price_type_state:   $(this).prop('checked'),
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
