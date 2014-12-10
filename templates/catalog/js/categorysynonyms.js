$(document).ready(function(){

	$("body").delegate(".do-filter-table", "change", function(){
		location.href = "/catalog/category-synonyms/" + $("#filter-updater").val() + "/" + $("#filter-distributor").val() + "/" + $("#filter-category").val() + "/";
		return true;
	});

	$("table").delegate(".do-link-category-synonym", "change", function(){
		$.post("/catalog/ajax/link-category-synonym/", {
			synonym: $(this).data('id'),
			category: $(this).val(),
			csrfmiddlewaretoken: '{{ csrf_token }}'
		},
		function(data) {
			if (null != data.status) {
				var notification = new NotificationFx({
					wrapper : document.body,
					message : '<p>' + data.message + '</p>',
					layout : 'growl',
					effect : 'genie',
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
