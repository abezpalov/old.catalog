$(document).ready(function(){


	// Добавить производителя
	$("#do-add-category").click(function() {

		// Отправляем данные
		$.post("/catalog/ajax/add/category/", {
			newCategoryName: $("#new-category-name").val(),
			newCategoryParent:  $("#new-category-parent").val(),
			csrfmiddlewaretoken: '{{ csrf_token }}'
		},

		// Обрабатываем ответ
		function(data) {
			if ('success' == data.status) {
				// TODO Обновить таблицу
				$("#categories-h").after('<tr><td colspan="">Succes</td></tr>');
				$("#new-category-name").val('');
				// TODO Вывести сообщение
			}
		}, "json");
		return false;
	});


	// Поменять статус производителя
	$("table").delegate(".do-switch-category-state", "click", function(){

		// Отправляем данные
		$.post("/catalog/ajax/switch/category/state/", {
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
		return true;
	});

});
