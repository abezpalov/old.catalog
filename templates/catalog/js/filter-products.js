// Открыть окно фильтра на закладке категорий
$("body").delegate("[data-do*='open-filter-products-category']", "click", function(){
	$('#dd-panel-category').addClass('active');
	$('#dd-panel-vendor').removeClass('active');
	$('#dd-panel-search').removeClass('active');
	$('#panel-category').addClass('active');
	$('#panel-vendor').removeClass('active');
	$('#panel-search').removeClass('active');
	$('#modal-filter-products').foundation('reveal', 'open');
	return false;
});


// Открыть окно фильтра на закладке производителей
$("body").delegate("[data-do*='open-filter-products-vendor']", "click", function(){
	$('#dd-panel-category').removeClass('active');
	$('#dd-panel-vendor').addClass('active');
	$('#dd-panel-search').removeClass('active');
	$('#panel-category').removeClass('active');
	$('#panel-vendor').addClass('active');
	$('#panel-search').removeClass('active');
	$('#modal-filter-products').foundation('reveal', 'open');
	return false;
});


// Открыть окно фильтра на закладке дополнительных параметров поиска
$("body").delegate("[data-do*='open-filter-products-search']", "click", function(){
	$('#dd-panel-category').removeClass('active');
	$('#dd-panel-vendor').removeClass('active');
	$('#dd-panel-search').addClass('active');
	$('#panel-category').removeClass('active');
	$('#panel-vendor').removeClass('active');
	$('#panel-search').addClass('active');
	$('#modal-filter-products').foundation('reveal', 'open');
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
