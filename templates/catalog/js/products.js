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
		$('#filter-items-category').removeClass('secondary');
		return false;
	});

	$("body").delegate("a[data-do*='filter-items-select-vendor']", "click", function(){
		$('#filter-items-selected-vendor').data('alias', $(this).data('alias'));
		$('#filter-items-selected-vendor').text($(this).text());
		$('#filter-items-vendor').removeClass('secondary');
		if ('none' == $('#filter-items-selected-category').data('id')) {
			$('#filter-items-selected-category').data('id', 'all');
			$('#filter-items-selected-category').text('все категории');
			$('#filter-items-category').removeClass('secondary');
		}
		return false;
	});

	$("body").delegate("button[data-do*='filter-items-run']", "click", function(){

		// Инициализируем переменные
		s = $('#filter-items-search-input').val();
		v = $('#filter-items-selected-vendor').data('alias');
		c = $('#filter-items-selected-category').data('id');

		// Формируем URL
		url = '/catalog/products/'
		if (s != '' && v != 'all' && v != 'none' && c != 'all' && c != 'none'){
			location.href = url + c + '/y/' + v + '/' + s + '/';
		} else if (s != '' && v != 'all' && v != 'none'){
			location.href = url + 'all/y/' + v + '/' + s + '/';
		} else if (s != '' && c != 'all' && c != 'none'){
			location.href = url + c + '/y/' + 'all/' + s + '/';
		} else if (v != 'all' && v != 'none' && c != 'all' && c != 'none'){
			location.href = url + c + '/y/' + v + '/';
		} else if (v != 'all' && v != 'none'){
			location.href = url + 'all/y/' + v + '/';
		} else if (c != 'all' && c != 'none'){
			location.href = url + c + '/y/';
		} else {
			alert ('Определите хотя бы одно условие выборки.');
		}
		$('#FilterItemsModal').foundation('reveal', 'close');
		return false;
	});

	$("body").delegate("button[data-do*='filter-items-cancel']", "click", function(){
		$('#FilterItemsModal').foundation('reveal', 'close');
		return false;
	});

});
