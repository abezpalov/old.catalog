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

	// TODO go filter

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

	$("body").delegate("a[data-do*='filter-select-category']", "click", function(){
		alert($(this).data('id'));

		// TODO select
		$('#FilterItemsModal').foundation('reveal', 'close');
		return false;
	});


	$("body").delegate("button[data-do*='filter-item-cancel']", "click", function(){
		$('#FilterItemsModal').foundation('reveal', 'close');
		return false;
	});

});
