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
				$("#new-vendor-tr").after('<tr><td><a href="/catalog/vendor/' + data.vendorAlias + '/">' + data.vendorName + '</a></td><td><div class="switch small"><input id="vendor-status-' + data.vendorId + '" data-id="' + data.vendorId + '" class="do-switch-vendor-status" type="checkbox" checked><label for="vendor-status-' + data.vendorId + '"></label></div></td></tr>');
				// TODO Вывести сообщение
			}
		}, "json");
	});


	// Очистить поле производителя
	$("#do-clear-vendor").on('click', function(){
		$("#new-vendor").val('');
	});


	// Поменять статус производителя
	$("table").delegate(".do-switch-vendor-state", "click", function(){
		// Отправляем данные
		$.post("/catalog/ajax/switch/vendor/state/", {
			id: $(this).data('id'),
			state: $(this).prop("checked"),
			csrfmiddlewaretoken: '{{ csrf_token }}'
		},
		// Обрабатываем ответ
		function(data) {
			if ('success' == data.status) {
				// TODO Вывести сообщение
			}
		}, "json");
	});

});
