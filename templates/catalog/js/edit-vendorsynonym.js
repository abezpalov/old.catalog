// Применение фильтра
$("body").delegate("[data-do='filter-vendor-synonyms']", "click", function(){
	location.href = "/catalog/vendor-synonyms/" + $("#filter-updater").val() + "/" + $("#filter-distributor").val() + "/" + $("#filter-vendor").val() + "/";
	return true;
});

{% if perms.catalog.add_vendorsynonym %}

// Открытие окна создания
$("body").delegate("[data-do='open-new-vendor-synonym']", "click", function(){

	// Заполняем значение полей
	$('#modal-edit-vendor-synonym-header').text('Добавить синоним производителя');
	$('#edit-vendor-synonym-id').val('0');
	$('#edit-vendor-synonym-name').val('');
	$('#edit-vendor-synonym-updater').val('0');
	$('#edit-vendor-synonym-distributor').val('0');
	$('#edit-vendor-synonym-vendor').val('0');

	// Открываем модальное окно
	$('#modal-edit-vendor-synonym').foundation('reveal', 'open');
	return false;
});

{% endif %}

{% if perms.catalog.change_vendorsynonym %}


// Открытие окна редактирования
$("body").delegate("[data-do='open-edit-vendor-synonym']", "click", function(){

	// Получаем информацию о категории
	$.post("/catalog/ajax/get-vendor-synonym/", {
		vendor_synonym_id:   $(this).data('id'),
		csrfmiddlewaretoken: '{{ csrf_token }}'
	},
	function(data) {
		if (null != data.status) {
			if ('success' == data.status){

				// Заполняем значение полей
				$('#modal-edit-vendor-synonym-header').text('Редактировать синоним производителя');
				$('#edit-vendor-synonym-id').val(data.vendor_synonym['id']);
				$('#edit-vendor-synonym-name').val(data.vendor_synonym['name'])
				$('#edit-vendor-synonym-updater').val(data.vendor_synonym['updater']['id'])
				$('#edit-vendor-synonym-distributor').val(data.vendor_synonym['distributor']['id'])
				$('#edit-vendor-synonym-vendor').val(data.vendor_synonym['vendor']['id'])

				// Открываем окно
				$('#modal-edit-vendor-synonym').foundation('reveal', 'open');

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
$("body").delegate("[data-do='edit-vendor-synonym-save']", "click", function(){

	// Отправляем запрос
	$.post("/catalog/ajax/save-vendor-synonym/", {
		vendor_synonym_id:             $('#edit-vendor-synonym-id').val(),
		vendor_synonym_name:           $('#edit-vendor-synonym-name').val(),
		vendor_synonym_updater_id:     $('#edit-vendor-synonym-updater').val(),
		vendor_synonym_distributor_id: $('#edit-vendor-synonym-distributor').val(),
		vendor_synonym_vendor_id:      $('#edit-vendor-synonym-vendor').val(),
		csrfmiddlewaretoken:           '{{ csrf_token }}'
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
				$("[data-vendor-synonym-name='" + $('#edit-vendor-synonym-id').val() + "']").text($('#edit-vendor-synonym-name').val());

				// Заполняем значение полей
				$('#edit-vendor-synonym-id').val('0');
				$('#edit-vendor-synonym-name').val('');
				$('#edit-vendor-synonym-updater').val('0');
				$('#edit-vendor-synonym-distributor').val('0');
				$('#edit-vendor-synonym-vendor').val('0');

				// Закрываем окно
				$('#modal-edit-vendor-synonym').foundation('reveal', 'close');
			}
		}
	}, "json");

	return false;
});


// Отмена редактирования
$("body").delegate("[data-do='edit-vendor-synonym-cancel']", "click", function(){

	// Заполняем значение полей
	$('#edit-vendor-synonym-id').val('0');
	$('#edit-vendor-synonym-name').val('');
	$('#edit-vendor-synonym-updater').val('0');
	$('#edit-vendor-synonym-distributor').val('0');
	$('#edit-vendor-synonym-vendor').val('0');

	// Закрываем окно
	$('#modal-edit-vendor-synonym').foundation('reveal', 'close');

	return false;
});

{% endif %}

{% if perms.catalog.delete_vendorsynonym %}


// Открытие модального окна удаления
$("body").delegate("[data-do='open-delete-vendor-synonym']", "click", function(){

	// Получаем информацию о категории
	$.post("/catalog/ajax/get-vendor-synonym/", {
		vendor_synonym_id:   $(this).data('id'),
		csrfmiddlewaretoken: '{{ csrf_token }}'
	},
	function(data) {
		if (null != data.status) {
			if ('success' == data.status){

				// Заполняем значение полей
				$('#delete-vendor-synonym-id').val(data.vendor_synonym['id']);
				$('#delete-vendor-synonym-name').text(data.vendor_synonym['name']);

				// Открываем окно
				$('#modal-delete-vendor-synonym').foundation('reveal', 'open');

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


// Удаление
$("body").delegate("[data-do='delete-vendor-synonym-apply']", "click", function(){

	// Отправляем запрос
	$.post("/catalog/ajax/delete-vendor-synonym/", {
		vendor_synonym_id:   $('#delete-vendor-synonym-id').val(),
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
			$('#modal-delete-vendor-synonym').foundation('reveal', 'close');

			// Обновляем страницу
			setTimeout(function () {location.reload();}, 3000);
		}
	}, "json");

	return false;
});

{% endif %}


// Привязка к одноимённому производителю
$("body").delegate("[data-do='link-vendor-synonym-same-vendor']", "click", function(){
	vendor_synonym_id = $(this).data('id');
	$.post("/catalog/ajax/link-vendor-synonym-same-vendor/", {
		vendor_synonym_id:   vendor_synonym_id,
		csrfmiddlewaretoken: '{{ csrf_token }}'
	},
	function(data) {
		if (null != data.status) {

			// Обновлем информацию на странице
			$("[data-vendor-synonym-id='" + vendor_synonym_id + "']").text(data.vendor.name);
			$("[data-vendor-synonym-id='" + vendor_synonym_id + "']").data('id', data.vendor.id);
			$("[data-vendor-synonym-id='" + vendor_synonym_id + "']").data('vendor-name', data.vendor.id);

			// TODO Обновляем список производителей в окне редактирования синонимов
		}
	}, "json");
	return false;
});
