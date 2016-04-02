// Применение фильтра
$("body").delegate("[data-do='filter-parameter-synonyms']", "click", function(){
	location.href = "/catalog/parameter-synonyms/" + $("#filter-updater").val() + "/" + $("#filter-distributor").val() + "/" + $("#filter-parameter").val() + "/";
	return true;
});

{% if perms.catalog.add_parametersynonym %}

// Открытие окна создания
$("body").delegate("[data-do='open-new-parameter-synonym']", "click", function(){

	// Заполняем значение полей
	$('#modal-edit-parameter-synonym-header').text('Добавить синоним производителя');
	$('#edit-parameter-synonym-id').val('0');
	$('#edit-parameter-synonym-name').val('');
	$('#edit-parameter-synonym-updater').val('0');
	$('#edit-parameter-synonym-distributor').val('0');
	$('#edit-parameter-synonym-parameter').val('0');

	// Открываем модальное окно
	$('#modal-edit-parameter-synonym').foundation('reveal', 'open');
	return false;
});

{% endif %}

{% if perms.catalog.change_parametersynonym %}


// Открытие окна редактирования
$("body").delegate("[data-do='open-edit-parameter-synonym']", "click", function(){

	// Получаем информацию о категории
	$.post("/catalog/ajax/get-parameter-synonym/", {
		parameter_synonym_id:   $(this).data('id'),
		csrfmiddlewaretoken: '{{ csrf_token }}'
	},
	function(data) {
		if (null != data.status) {
			if ('success' == data.status){

				// Заполняем значение полей
				$('#modal-edit-parameter-synonym-header').text('Редактировать синоним параметра');
				$('#edit-parameter-synonym-id').val(data.parameter_synonym['id']);
				$('#edit-parameter-synonym-name').val(data.parameter_synonym['name'])
				$('#edit-parameter-synonym-updater').val(data.parameter_synonym['updater']['id'])
				$('#edit-parameter-synonym-distributor').val(data.parameter_synonym['distributor']['id'])
				$('#edit-parameter-synonym-parameter').val(data.parameter_synonym['parameter']['id'])

				// Открываем окно
				$('#modal-edit-parameter-synonym').foundation('reveal', 'open');

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
$("body").delegate("[data-do='edit-parameter-synonym-save']", "click", function(){

	// Отправляем запрос
	$.post("/catalog/ajax/save-parameter-synonym/", {
		parameter_synonym_id             : $('#edit-parameter-synonym-id').val(),
		parameter_synonym_name           : $('#edit-parameter-synonym-name').val(),
		parameter_synonym_updater_id     : $('#edit-parameter-synonym-updater').val(),
		parameter_synonym_distributor_id : $('#edit-parameter-synonym-distributor').val(),
		parameter_synonym_parameter_id   : $('#edit-parameter-synonym-parameter').val(),
		csrfmiddlewaretoken              : '{{ csrf_token }}'
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
				$("[data-parameter-synonym-name='" + $('#edit-parameter-synonym-id').val() + "']").text($('#edit-parameter-synonym-name').val());

				// Заполняем значение полей
				$('#edit-parameter-synonym-id').val('0');
				$('#edit-parameter-synonym-name').val('');
				$('#edit-parameter-synonym-updater').val('0');
				$('#edit-parameter-synonym-distributor').val('0');
				$('#edit-parameter-synonym-parameter').val('0');

				// Закрываем окно
				$('#modal-edit-parameter-synonym').foundation('reveal', 'close');
			}
		}
	}, "json");

	return false;
});


// Отмена редактирования
$("body").delegate("[data-do='edit-parameter-synonym-cancel']", "click", function(){

	// Заполняем значение полей
	$('#edit-parameter-synonym-id').val('0');
	$('#edit-parameter-synonym-name').val('');
	$('#edit-parameter-synonym-updater').val('0');
	$('#edit-parameter-synonym-distributor').val('0');
	$('#edit-parameter-synonym-parameter').val('0');

	// Закрываем окно
	$('#modal-edit-parameter-synonym').foundation('reveal', 'close');

	return false;
});

{% endif %}

{% if perms.catalog.delete_parametersynonym %}


// Открытие модального окна удаления
$("body").delegate("[data-do='open-delete-parameter-synonym']", "click", function(){

	// Получаем информацию о категории
	$.post("/catalog/ajax/get-parameter-synonym/", {
		parameter_synonym_id:   $(this).data('id'),
		csrfmiddlewaretoken: '{{ csrf_token }}'
	},
	function(data) {
		if (null != data.status) {
			if ('success' == data.status){

				// Заполняем значение полей
				$('#delete-parameter-synonym-id').val(data.parameter_synonym['id']);
				$('#delete-parameter-synonym-name').text(data.parameter_synonym['name']);

				// Открываем окно
				$('#modal-delete-parameter-synonym').foundation('reveal', 'open');

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
$("body").delegate("[data-do='delete-parameter-synonym-apply']", "click", function(){

	// Отправляем запрос
	$.post("/catalog/ajax/delete-parameter-synonym/", {
		parameter_synonym_id:   $('#delete-parameter-synonym-id').val(),
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
			$('#modal-delete-parameter-synonym').foundation('reveal', 'close');

			// Обновляем страницу
			setTimeout(function () {location.reload();}, 3000);
		}
	}, "json");

	return false;
});

{% endif %}


// Привязка к одноимённому производителю
$("body").delegate("[data-do='link-parameter-synonym-same-parameter']", "click", function(){
	parameter_synonym_id = $(this).data('id');
	$.post("/catalog/ajax/link-parameter-synonym-same-parameter/", {
		parameter_synonym_id : parameter_synonym_id,
		csrfmiddlewaretoken  : '{{ csrf_token }}'
	},
	function(data) {
		if (null != data.status) {

			// Обновлем информацию на странице
			$("[data-parameter-synonym-id='" + parameter_synonym_id + "']").text(data.parameter.name);
			$("[data-parameter-synonym-id='" + parameter_synonym_id + "']").data('id', data.parameter.id);
			$("[data-parameter-synonym-id='" + parameter_synonym_id + "']").data('parameter-name', data.parameter.id);

			// TODO Обновляем список параметров в окне редактирования синонимов
		}
	}, "json");
	return false;
});
