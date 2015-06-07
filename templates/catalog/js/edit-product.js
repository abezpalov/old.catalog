{% if perms.catalog.change_product %}


// Открытие окна редактирования продукта (существующий)
$("body").delegate("[data-do*='open-edit-product']", "click", function(){

	// Получаем информацию о продукте
	$.post("/catalog/ajax/get-product/", {
		product_id: $(this).data('id'),
		csrfmiddlewaretoken: '{{ csrf_token }}'
	},
	function(data) {
		if (null != data.status) {
			if ('success' == data.status){

				// Заполняем значение полей
				$('#edit-product-id').val(data.product_id);
				$('#edit-product-name').val(data.product_name)
				$('#edit-product-article').val(data.product_article)
				$('#edit-product-vendor').val(data.product_vendor_id)
				$('#edit-product-category').val(data.product_category_id)
				$('#edit-product-description').val(data.product_description)
				$('#edit-product-double').val(data.product_duble_id)
				$('#edit-product-state').prop('checked', data.product_state)

				// Открываем окно
				$('#modal-edit-product').foundation('reveal', 'open');

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


// Сохранение продукта
$("body").delegate("[data-do*='edit-product-save']", "click", function(){

	// Отправляем запрос
	$.post("/catalog/ajax/save-product/", {
		product_id:          $('#edit-product-id').val(),
		product_name:        $('#edit-product-name').val(),
		product_article:     $('#edit-product-article').val(),
		product_vendor_id:   $('#edit-product-vendor').val(),
		product_category_id: $('#edit-product-category').val(),
		product_description: $('#edit-product-description').val(),
		product_duble_id:    $('#edit-product-double').val(),
		product_state:       $('#edit-product-state').prop('checked'),
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

				// Закрываем окно
				$('#modal-edit-product').foundation('reveal', 'close');

				// Обновляем страницу
				// TODO Добаботать обновление данных без перезагрузки
				setTimeout(function () {location.reload();}, 3000);
			}
		}
	}, "json");

	return false;
});


// Отмена редактирования продукта
$("body").delegate("[data-do*='edit-product-cancel']", "click", function(){

	// Заполняем значение полей
	$('#edit-product-id').val('0');
	$('#edit-product-name').val('')
	$('#edit-product-article').val('')
	$('#edit-product-vendor').val('0')
	$('#edit-product-category').val('0')
	$('#edit-product-description').val('')
	$('#edit-product-double').val('')
	$('#edit-product-state').prop('checked', false)

	// Закрываем окно
	$('#modal-edit-product').foundation('reveal', 'close');

	return false;
});


{% endif %}

{% if perms.catalog.delete_product %}


// Открытие модального окна удаления продукта
$("body").delegate("[data-do*='open-product-trash']", "click", function(){

	// Заполняем значение полей
	$('#trash-product-id').val($(this).data('id'));

	// Открываем окно
	$('#modal-trash-product').foundation('reveal', 'open');

	return false;
});


// Удаление продукта
$("body").delegate("[data-do*='trash-product']", "click", function(){

	// Отправляем запрос
	$.post("/catalog/ajax/trash-product/", {
		product_id:          $('#trash-product-id').val(),
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
			$('#modal-trash-product').foundation('reveal', 'close');

			// Обновляем страницу
			setTimeout(function () {location.reload();}, 3000);
		}
	}, "json");

	return false;
});

{% endif %}
