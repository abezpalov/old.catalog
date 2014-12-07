$(document).ready(function(){


	// Добавить производителя
	$("#do-add-category").click(function() {

		// Отправляем данные
		$.post("/catalog/ajax/add-category/", {
			newCategoryName: $("#new-category-name").val(),
			newCategoryParent:  $("#new-category-parent").val(),
			csrfmiddlewaretoken: '{{ csrf_token }}'
		},

		// Обрабатываем ответ
		function(data) {
			if (null != data.status) {
				// TODO Обновить таблицу
				$("#categories-h").after('<tr><td colspan="">Succes</td></tr>');
				$("#new-category-name").val('');

				// TODO Вывести сообщение
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
		}, "json");
		location.reload();
		return false;
	});


	// Поменять статус производителя
	$("body").delegate(".do-switch-category-state", "click", function(){

		// Отправляем данные
		$.post("/catalog/ajax/switch-category-state/", {
			id: $(this).data('id'),
			state: $(this).prop("checked"),
			csrfmiddlewaretoken: '{{ csrf_token }}'
		},

		// Обрабатываем ответ
		function(data) {
			if (null != data.status) {
				// TODO Вывести сообщение
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
		}, "json");
		return true;
	});

});
