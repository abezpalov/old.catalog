{% if perms.catalog.add_category %}

// Открытие окна редактирования категории (новая)
$("body").delegate("[data-do='open-new-category']", "click", function(){

	// Заполняем значение полей
	$('#modal-edit-category-header').text('Добавить категорию');
	$('#edit-category-id').val('0');
	$('#edit-category-name').val('');
	$('#edit-category-alias').val('');
	$('#edit-category-parent').val('0');
	$('#edit-category-description').val('');
	$('#edit-category-state').prop('checked', false);

	// Открываем модальное окно
	$('#modal-edit-category').foundation('reveal', 'open');
	return false;
});

{% endif %}

{% if perms.catalog.change_category %}


// Открытие окна редактирования категории (существующая)
$("body").delegate("[data-do='open-edit-category']", "click", function(){

	// Получаем информацию о категории
	$.post("/catalog/ajax/get-category/", {
		category_id:         $(this).data('id'),
		csrfmiddlewaretoken: '{{ csrf_token }}'
	},
	function(data) {
		if (null != data.status) {
			if ('success' == data.status){

				// Заполняем значение полей
				$('#modal-edit-category-header').text('Редактировать категорию');
				$('#edit-category-id').val(data.category['id']);
				$('#edit-category-name').val(data.category['name'])
				$('#edit-category-alias').val(data.category['alias'])
				$('#edit-category-parent').val(data.category['parent']['id'])
				$('#edit-category-description').val(data.category['description'])
				$('#edit-category-state').prop('checked', data.category['state'])

				// Открываем окно
				$('#modal-edit-category').foundation('reveal', 'open');

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


// Сохранение категории
$("body").delegate("[data-do='edit-category-save']", "click", function(){

	// Отправляем запрос
	$.post("/catalog/ajax/save-category/", {
		category_id:           $('#edit-category-id').val(),
		category_name:         $('#edit-category-name').val(),
		category_alias:        $('#edit-category-alias').val(),
		category_parent_id:    $('#edit-category-parent').val(),
		category_description:  $('#edit-category-description').val(),
		category_state:        $('#edit-category-state').prop('checked'),
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
				$("[data-category-name='" + $('#edit-category-id').val() + "']").text($('#edit-category-name').val());
				$("[data-category-state='" + $('#edit-category-id').val() + "']").prop('checked', $('#edit-category-state').prop('checked'));

				// Заполняем значение полей
				$('#edit-category-id').val('0');
				$('#edit-category-name').val('');
				$('#edit-category-alias').val('');
				$('#edit-category-parent').val('');
				$('#edit-category-description').val('');
				$('#edit-category-state').prop('checked', false);

				// Обновляем страницу
				setTimeout(function () {location.reload();}, 3000);

				// Закрываем окно
				$('#modal-edit-category').foundation('reveal', 'close');
			}
		}
	}, "json");

	return false;
});


// Отмена редактирования категории
$("body").delegate("[data-do='edit-category-cancel']", "click", function(){

	// Заполняем значение полей
	$('#edit-category-id').val('0');
	$('#edit-category-name').val('');
	$('#edit-category-alias').val('');
	$('#edit-category-parent').val('0');
	$('#edit-category-description').val('');
	$('#edit-category-state').prop('checked', false);

	// Закрываем окно
	$('#modal-edit-category').foundation('reveal', 'close');

	return false;
});

{% endif %}

{% if perms.catalog.delete_category %}


// Открытие модального окна удаления категории
$("body").delegate("[data-do='open-delete-category']", "click", function(){

	// Получаем информацию о категории
	$.post("/catalog/ajax/get-category/", {
		category_id:         $(this).data('id'),
		csrfmiddlewaretoken: '{{ csrf_token }}'
	},
	function(data) {
		if (null != data.status) {
			if ('success' == data.status){

				// Заполняем значение полей
				$('#delete-category-id').val(data.category['id']);
				$('#delete-category-name').text(data.category['name'])

				// Открываем окно
				$('#modal-delete-category').foundation('reveal', 'open');

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


// Удаление категории
$("body").delegate("[data-do='delete-category-apply']", "click", function(){

	// Отправляем запрос
	$.post("/catalog/ajax/delete-category/", {
		category_id:         $('#delete-category-id').val(),
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
			$('#modal-delete-category').foundation('reveal', 'close');

			// Обновляем страницу
			setTimeout(function () {location.reload();}, 3000);
		}
	}, "json");

	return false;
});

{% endif %}

{% if perms.catalog.change_category %}


// Смена статуса производителя
$("body").delegate("[data-do='switch-category-state']", "click", function(){

	// Отправляем запрос
	$.post("/catalog/ajax/switch-category-state/", {
		category_id:         $(this).data('id'),
		category_state:      $(this).prop('checked'),
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
