// Открыть окно фильтра на закладке категорий
$("body").delegate("[data-do*='open-filter-products-category']", "click", function(){
	$('#modal-filter-products').foundation('reveal', 'open');
	$('#dd-panel-category').addClass('active');
	$('#dd-panel-vendor').removeClass('active');
	$('#dd-panel-search').removeClass('active');
	$('#panel-category').addClass('active');
	$('#panel-vendor').removeClass('active');
	$('#panel-search').removeClass('active');
	return false;
});


// Открыть окно фильтра на закладке производителей
$("body").delegate("[data-do*='open-filter-products-vendor']", "click", function(){
	$('#modal-filter-products').foundation('reveal', 'open');
	$('#dd-panel-category').removeClass('active');
	$('#dd-panel-vendor').addClass('active');
	$('#dd-panel-search').removeClass('active');
	$('#panel-category').removeClass('active');
	$('#panel-vendor').addClass('active');
	$('#panel-search').removeClass('active');
	return false;
});


// Открыть окно фильтра на закладке дополнительных параметров поиска
$("body").delegate("[data-do*='open-filter-products-search']", "click", function(){
	$('#modal-filter-products').foundation('reveal', 'open');
	$('#dd-panel-category').removeClass('active');
	$('#dd-panel-vendor').removeClass('active');
	$('#dd-panel-search').addClass('active');
	$('#panel-category').removeClass('active');
	$('#panel-vendor').removeClass('active');
	$('#panel-search').addClass('active');
	return false;
});


// Открытие/закрытие ветви категорий
$("body").delegate("[data-do*='switch-li-status']", "click", function(){
	if ($(this).data('state') == 'closed') {
		$(this).parent("li").removeClass('closed');
		$(this).parent("li").addClass('opened');
		$(this).removeClass('fa-plus-square-o');
		$(this).addClass('fa-minus-square-o');
		$(this).data('state', 'opened');
	} else {
		$(this).parent("li").removeClass('opened');
		$(this).parent("li").addClass('closed');
		$(this).removeClass('fa-minus-square-o');
		$(this).addClass('fa-plus-square-o');
		$(this).data('state', 'closed');
	}
	return false;
});


// Выбор категории
$("body").delegate("[data-do*='filter-products-select-category']", "click", function(){
	$('#filter-products-selected-category').data('id', $(this).data('id'));
	$('#filter-products-selected-category').text($(this).text());
	if ($(this).data('id') == ''){
		$('#filter-products-category').addClass('secondary');
	} else {
		$('#filter-products-category').removeClass('secondary');
	}
	return false;
});


// Выбор производителя
$("body").delegate("[data-do*='filter-products-select-vendor']", "click", function(){
	$('#filter-products-selected-vendor').data('alias', $(this).data('alias'));
	$('#filter-products-selected-vendor').text($(this).text());
	if ($(this).data('alias') == ''){
		$('#filter-products-vendor').addClass('secondary');
	} else {
		$('#filter-products-vendor').removeClass('secondary');
	}
	return false;
});


// Фильтр списка производителей
$("body").delegate("[data-do*='filter-products-filter-vendors']", "keypress", function(e){
	var filter_text = $.trim($('#filter-products-filter-vendors').val().toLowerCase());
	var key = e.which;
	if(key == 13) {
		// Скрываем всех, кто не соответствует запросу
		if (filter_text != ''){
			$("div[data-is*='vendor-selector']").each(function(i, e){
				if ($(e).text().toLowerCase().search(filter_text) == -1) {
					$(e).addClass('hidden');
				} else {
					$(e).removeClass('hidden');
				}
			});
		} else {
			$("div[data-is*='vendor-selector']").removeClass('hidden');
		}
		return false;
	}
});


// Введена строка поиска
$("body").delegate("#filter-products-search-input", "change", function(){
	if ($('#filter-products-search-input').val() == ''){
		$('#filter-products-search').addClass('secondary');
	} else {
		$('#filter-products-search').removeClass('secondary');
	}
});


// Применение параметров фильтра
$("body").delegate("[data-do*='filter-products-apply']", "click", function(){

	// Инициализируем переменные
	ct = $('#filter-products-selected-category').data('id');
	ch = $('#filter-products-selected-childs').prop('checked');
	vn = $('#filter-products-selected-vendor').data('alias');
	sr = $.trim($('#filter-products-search-input').val());

	// Формируем URL
	url = '/catalog/products/'

	// Категория
	if (ct != ''){
		url = url + 'c/' + ct;
		if (ch == true) {
			url = url + '-y/';
		} else {
			url = url + '-n/';
		}
	}

	// Производитель
	if (vn != ''){
		url = url + vn + '/';
	}

	// Строка поиска
	if (sr != ''){
		url = url + 'search/' + sr + '/';
	}

	// Переходим по ссылке
	if (ct == '' && vn == '' && sr == '') {
		alert ('Определите хотя бы одно условие выборки.');
	} else {
		$('#modal-filter-products').foundation('reveal', 'close');
		location.href = url;
	}
});


// Отмена применения параметров фильтра
$("body").delegate("[data-do*='filter-products-cancel']", "click", function(){
	$('#modal-filter-products').foundation('reveal', 'close');
	return false;
});


// Синхронизация полей поиска (только сверху вниз)
$("body").delegate('#top-search-input', "change", function(){
	$('#filter-products-search-input').val($('#top-search-input').val())
	if ($('#filter-products-search-input').val() == ''){
		$('#filter-products-search').addClass('secondary');
	} else {
		$('#filter-products-search').removeClass('secondary');
	}
});


// Просмотр партий
$("body").delegate("[data-do*='open-view-parties']", "click", function(){

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
				$('#ViewPartiesModalContent').html(html_data);
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
