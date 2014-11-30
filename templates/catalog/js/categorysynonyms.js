$(document).ready(function(){

	// Применить фильтр
	$("body").delegate(".do-filter-table", "change", function(){
		location.href = "/catalog/category-synonyms/" + $("#filter-updater").val() + "/" + $("#filter-distributor").val() + "/" + $("#filter-category").val() + "/";
		return true;
	});

	// Привязать синоним
	$("table").delegate(".do-link-category-synonym", "change", function(){

		// Отправляем данные
		$.post("/catalog/ajax/link/category/synonym/", {
			synonym: $(this).data('id'),
			category: $(this).val(),
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
