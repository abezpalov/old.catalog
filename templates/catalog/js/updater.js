$(document).ready(function(){


	// Добавить производителя
	$("#do-save-updater").click(function() {

		// Отправляем данные
		$.post("/catalog/ajax/save-updater/", {
			id: '{{ updater.id }}',
			name: $("#updater-name").val(),
			alias: $("#updater-alias").val(),
			login: $("#updater-login").val(),
			password: $("#updater-password").val(),
			csrfmiddlewaretoken: '{{ csrf_token }}'
		},

		// Обрабатываем ответ
		function(data) {
			if (null != data.status) {
				// TODO Обновить содержимое
				// $("#categories-h").after('<tr><td colspan="">Succes</td></tr>');

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
		return false;
	});

});
