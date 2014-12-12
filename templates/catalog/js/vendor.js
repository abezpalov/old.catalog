$(document).ready(function(){

	$("#do-save-vendor").click(function() {
		$.post("/catalog/ajax/save-vendor/", {
			id: '{{ vendor.id }}',
			name: $("#vendor-name").val(),
			alias: $("#vendor-alias").val(),
			login: $("#vendor-description").val(),
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
