// Просмотр партий
$("body").delegate("[data-do='open-view-parties']", "click", function(){

	// Очищаем содержимое
	$('#modal-view-parties-content').html('')

	// Запрашиваем партии на сервере
	$.post("/catalog/ajax/get-parties/", {
		product_id:          $(this).data('id'),
		csrfmiddlewaretoken: '{{ csrf_token }}'
	},
	function(data) {
		if (null != data.status) {
			if ('success' == data.status){
				html_data = ""
				head = "<p>" + data.product['product_name'] + "<br/>Артикул:&nbsp;" + data.product['product_article'] + "<br/>Производитель:&nbsp;" + data.product['vendor_name'] + "</p>"

				// TODO Обработать и вывести данные
				// Если партии товара есть
				if (0 < data.len) {
					// Если получен полный набор данных
					if (true == data.access) {
						thead = "<tr><th>Склад</th><th>Срок поставки</th><th>Количество</th><th>Цена<br/>(вход)</th><th>Цена<br/>(выход)</th></tr>"
						tbody = ""
						for(i = 0; i < data.len; i++) {
							tr = "<tr><td>" + data.items[i]['stock'] + "</td><td>" + data.items[i]['delivery_time_min'] + "&ndash;" + data.items[i]['delivery_time_max'] + "&nbsp;дней</td><td>" + data.items[i]['quantity'] + "</td><td>" + data.items[i]['price'] + "</td><td>" + data.items[i]['price_out'] + "</td></tr>";
							tbody = tbody + tr;
						}
					// Если получен сокращенный набор данных
					} else {
						thead = "<tr><th>Срок поставки</th><th>Количество</th><th>Цена</th></tr>"
						tbody = ""
						for(i = 0; i < data.len; i++) {
							tr = "<tr><td>" + data.items[i]['delivery_time_min'] + "&ndash;" + data.items[i]['delivery_time_max'] + "&nbsp;дней</td><td>" + data.items[i]['quantity'] + "</td><td>" + data.items[i]['price_out'] + "</td></tr>";
							tbody = tbody + tr;
						}
					}
					html_data = head + "<table><thead>" + thead + "</thead><tbody>" + tbody + "</tbody></table>";

				} else {
					html_data = head + '<div class="panel">Товар отсутствует.</div>';
				}
				$('#modal-view-parties-content').html(html_data);
			} else {
				var notification = new NotificationFx({
					wrapper: document.body,
					message: '<p>' + data.message + '</p>',
					layout: 'growl',
					effect: 'genie',
					type: data.status,
					ttl: 3000,
					onClose: function() { return false; },
					onOpen: function() { return false; }
				});
				notification.show();
			}
		}
	}, "json");

	// Открываем модальное окно
	$('#modal-view-parties').foundation('reveal', 'open');
	return false;
});
