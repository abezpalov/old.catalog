// Применение фильтра
$("body").delegate("[data-do='filter-category-synonyms']", "click", function(){
	location.href = "/catalog/category-synonyms/" + $("#filter-updater").val() + "/" + $("#filter-distributor").val() + "/" + $("#filter-category").val() + "/";
	return true;
});

{% if perms.catalog.add_categorysynonym %}

// Открытие окна создания
$("body").delegate("[data-do='open-new-category-synonym']", "click", function(){

	// Заполняем значение полей
	$('#modal-edit-category-synonym-header').text('Добавить синоним категории');
	$('#edit-category-synonym-id').val('0');
	$('#edit-category-synonym-name').val('');
	$('#edit-category-synonym-updater').val('0');
	$('#edit-category-synonym-distributor').val('0');
	$('#edit-category-synonym-category').val('0');

	// Открываем модальное окно
	$('#modal-edit-category-synonym').foundation('reveal', 'open');
	return false;
});

{% endif %}

{% if perms.catalog.change_categorysynonym %}


// Открытие окна редактирования
$("body").delegate("[data-do='open-edit-category-synonym']", "click", function(){

	// Получаем информацию о категории
	$.post("/catalog/ajax/get-category-synonym/", {
		category_synonym_id: $(this).data('id'),
		csrfmiddlewaretoken: '{{ csrf_token }}'
	},
	function(data) {
		if (null != data.status) {
			if ('success' == data.status){

				// Заполняем значение полей
				$('#modal-edit-category-synonym-header').text('Редактировать категорию');
				$('#edit-category-synonym-id').val(data.category_synonym['id']);
				$('#edit-category-synonym-name').val(data.category_synonym['name'])
				$('#edit-category-synonym-updater').val(data.category_synonym['updater']['id'])
				$('#edit-category-synonym-distributor').val(data.category_synonym['distributor']['id'])
				$('#edit-category-synonym-category').val(data.category_synonym['category']['id'])

				// Открываем окно
				$('#modal-edit-category-synonym').foundation('reveal', 'open');

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
$("body").delegate("[data-do='edit-category-synonym-save']", "click", function(){

	// Отправляем запрос
	$.post("/catalog/ajax/save-category-synonym/", {
		category_synonym_id:             $('#edit-category-synonym-id').val(),
		category_synonym_name:           $('#edit-category-synonym-name').val(),
		category_synonym_updater_id:     $('#edit-category-synonym-updater').val(),
		category_synonym_distributor_id: $('#edit-category-synonym-distributor').val(),
		category_synonym_category_id:    $('#edit-category-synonym-category').val(),
		csrfmiddlewaretoken:             '{{ csrf_token }}'
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
				$("[data-category-synonym-name='" + $('#edit-category-synonym-id').val() + "']").text($('#edit-category-synonym-name').val());

				// Заполняем значение полей
				$('#edit-category-synonym-id').val('0');
				$('#edit-category-synonym-name').val('');
				$('#edit-category-synonym-updater').val('0');
				$('#edit-category-synonym-distributor').val('0');
				$('#edit-category-synonym-category').val('0');

				// Закрываем окно
				$('#modal-edit-category-synonym').foundation('reveal', 'close');
			}
		}
	}, "json");

	return false;
});


// Отмена редактирования
$("body").delegate("[data-do='edit-category-synonym-cancel']", "click", function(){

	// Заполняем значение полей
	$('#edit-category-synonym-id').val('0');
	$('#edit-category-synonym-name').val('');
	$('#edit-category-synonym-updater').val('0');
	$('#edit-category-synonym-distributor').val('0');
	$('#edit-category-synonym-category').val('0');

	// Закрываем окно
	$('#modal-edit-category-synonym').foundation('reveal', 'close');

	return false;
});

{% endif %}

{% if perms.catalog.delete_categorysynonym %}


// Открытие модального окна удаления
$("body").delegate("[data-do='open-delete-category-synonym']", "click", function(){

	// Получаем информацию о категории
	$.post("/catalog/ajax/get-category-synonym/", {
		category_synonym_id: $(this).data('id'),
		csrfmiddlewaretoken: '{{ csrf_token }}'
	},
	function(data) {
		if (null != data.status) {
			if ('success' == data.status){

				// Заполняем значение полей
				$('#delete-category-synonym-id').val(data.category_synonym['id']);
				$('#delete-category-synonym-name').text(data.category_synonym['name'])

				// Открываем окно
				$('#modal-delete-category-synonym').foundation('reveal', 'open');

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
$("body").delegate("[data-do='delete-category-synonym-apply']", "click", function(){

	// Отправляем запрос
	$.post("/catalog/ajax/delete-category-synonym/", {
		category_synonym_id: $('#delete-category-synonym-id').val(),
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
			$('#modal-delete-category-synonym').foundation('reveal', 'close');

			// Обновляем страницу
			setTimeout(function () {location.reload();}, 3000);
		}
	}, "json");

	return false;
});

{% endif %}
