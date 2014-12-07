$(document).ready(function(){

	// Поменять статус загрузчика
	$("body").delegate(".do-switch-updater-state", "click", function(){

		// Отправляем данные
		$.post("/catalog/ajax/switch-updater-state/", {
			id: $(this).data('id'),
			state: $(this).prop("checked"),
			csrfmiddlewaretoken: '{{ csrf_token }}'
		},

		// Обрабатываем ответ
		function(data) {
			if (null != data.status) {
				// Вывести сообщение
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
