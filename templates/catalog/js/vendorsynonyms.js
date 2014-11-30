$(document).ready(function(){

	// Применить фильтр
	$("body").delegate(".do-filter-table", "change", function(){
		location.href = "/catalog/vendor-synonyms/" + $("#filter-updater").val() + "/" + $("#filter-distributor").val() + "/" + $("#filter-vendor").val() + "/";
		return true;
	});

	// Привязать синоним
	$("table").delegate(".do-link-vendor-synonym", "change", function(){

		// Отправляем данные
		$.post("/catalog/ajax/link/vendor/synonym/", {
			synonym: $(this).data('id'),
			vendor: $(this).val(),
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

	// Привязать синоним к одноименному производителю
	$("table").delegate(".do-link-vendor-same-synonym", "click", function(){

		// Отправляем данные
		$.post("/catalog/ajax/link/vendor/same/synonym/", {
			synonym: $(this).data('id'),
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
		location.reload();
		return false;
	});

});
