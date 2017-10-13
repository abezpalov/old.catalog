// Поиск по верхней строке поиска
$('#top-search-input').keypress(function (e) {
	var key = e.which;
	if(key == 13) {
        if ($.trim($('#top-search-input').val()) != ''){
    		location.href = '/catalog/products/search=' + $.trim($('#top-search-input').val()) + '/';
    	}
	return false;
	}
});
