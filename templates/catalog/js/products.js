$(document).ready(function(){

	$("body").delegate("button[data-do*='open-filter-items-category']", "click", function(){
		$('#FilterItemsModal').foundation('reveal', 'open');
		$('#CategoryPanelDD').addClass('active');
		$('#VendorPanelDD').removeClass('active');
		$('#SearchPanelDD').removeClass('active');
		$('#CategoryPanel').addClass('active');
		$('#VendorPanel').removeClass('active');
		$('#SearchPanel').removeClass('active');
		return false;
	});

	$("body").delegate("button[data-do*='open-filter-items-vendor']", "click", function(){
		$('#FilterItemsModal').foundation('reveal', 'open');
		$('#CategoryPanelDD').removeClass('active');
		$('#VendorPanelDD').addClass('active');
		$('#SearchPanelDD').removeClass('active');
		$('#CategoryPanel').removeClass('active');
		$('#VendorPanel').addClass('active');
		$('#SearchPanel').removeClass('active');
		return false;
	});

	$("body").delegate("button[data-do*='open-filter-items-search']", "click", function(){
		$('#FilterItemsModal').foundation('reveal', 'open');
		$('#CategoryPanelDD').removeClass('active');
		$('#VendorPanelDD').removeClass('active');
		$('#SearchPanelDD').addClass('active');
		$('#CategoryPanel').removeClass('active');
		$('#VendorPanel').removeClass('active');
		$('#SearchPanel').addClass('active');
		return false;
	});

	$("body").delegate("i[data-do*='switch-li-status']", "click", function(){
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

	$("body").delegate("a[data-do*='filter-items-select-category']", "click", function(){
		$('#filter-items-selected-category').data('id', $(this).data('id'));
		$('#filter-items-selected-category').text($(this).text());
		if ($(this).data('id') == ''){
			$('#filter-items-category').addClass('secondary');
		} else {
			$('#filter-items-category').removeClass('secondary');
		}
		return false;
	});

	$("body").delegate("a[data-do*='filter-items-select-vendor']", "click", function(){
		$('#filter-items-selected-vendor').data('alias', $(this).data('alias'));
		$('#filter-items-selected-vendor').text($(this).text());
		if ($(this).data('alias') == ''){
			$('#filter-items-vendor').addClass('secondary');
		} else {
			$('#filter-items-vendor').removeClass('secondary');
		}
		return false;
	});

	$("body").delegate("#filter-items-search-input", "change", function(){
		if ($('#filter-items-search-input').val() == ''){
			$('#filter-items-search').addClass('secondary');
		} else {
			$('#filter-items-search').removeClass('secondary');
		}
	});

	$("body").delegate("button[data-do*='filter-items-run']", "click", function(){

		// Инициализируем переменные
		ct = $('#filter-items-selected-category').data('id');
		ch = $('#filter-items-selected-childs').prop('checked');
		vn = $('#filter-items-selected-vendor').data('alias');
		sr = $('#filter-items-search-input').val();

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
		if (ct == '' || vn == '' || sr == '') {
			$('#FilterItemsModal').foundation('reveal', 'close');
			location.href = url;
		} else {
			alert ('Определите хотя бы одно условие выборки.');
		}
	});

	$("body").delegate("button[data-do*='filter-items-cancel']", "click", function(){
		$('#FilterItemsModal').foundation('reveal', 'close');
		return false;
	});

	$('#top-search-input').keypress(function (e) {
		var key = e.which;
		if(key == 13) {
			$('#top-search-button').click();
			return false;
		}
	});

	$("body").delegate('#top-search-input', "change", function(){
		$('#filter-items-search-input').val($('#top-search-input').val())
		if ($('#filter-items-search-input').val() == ''){
			$('#filter-items-search').addClass('secondary');
		} else {
			$('#filter-items-search').removeClass('secondary');
		}
	});

	$("body").delegate("#top-search-button", "click", function(){
		if ($('#top-search-input').val() != ''){
			location.href = '/catalog/products/search/' + $('#top-search-input').val() + '/';
		}
		return false;
	});
});
