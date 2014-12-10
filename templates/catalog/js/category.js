$(document).ready(function(){

	$("#do-save-category").click(function() {
		$.post("/catalog/ajax/save-category/", {
			id: '{{ category.id }}',
			name: $("#category-name").val(),
			alias: $("#category-alias").val(),
			login: $("#category-description").val(),
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
		return false;
	});
});
