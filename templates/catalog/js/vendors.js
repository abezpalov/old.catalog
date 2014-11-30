$(document).ready(function(){


	// Добавить производителя
	$("#do-add-vendor").click(function() {

		// Отправляем данные
		$.post("/catalog/ajax/add/vendor/", {
			new_vendor: $("#new-vendor").val(),
			csrfmiddlewaretoken: '{{ csrf_token }}'
		},

		// Обрабатываем ответ
		function(data) {
			if ('success' == data.status) {

				// Вывести сообщение
				var notification = new NotificationFx({
					wrapper : document.body,
					message : '<p>' + data.message + '</p>',
					layout : 'attached',
					effect : 'flip',
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
	$("body").delegate(".do-switch-vendor-state", "click", function(){

		// Отправляем данные
		$.post("/catalog/ajax/switch/vendor/state/", {
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
					layout : 'attached',
					effect : 'flip',
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
