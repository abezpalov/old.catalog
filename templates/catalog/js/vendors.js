$(document).ready(function(){


	$("#do-add-vendor").click(function() {
		$.post("/catalog/ajax/add-vendor/", {
			new_vendor: $("#new-vendor").val(),
			csrfmiddlewaretoken: '{{ csrf_token }}'
		},

		function(data) {
			if ('success' == data.status) {
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
				setTimeout(function () {location.reload();}, 3000);
			}
		}, "json");
		return false;
	});


	$("body").delegate(".do-switch-vendor-state", "click", function(){
		$.post("/catalog/ajax/switch-vendor-state/", {
			id: $(this).data('id'),
			state: $(this).prop("checked"),
			csrfmiddlewaretoken: '{{ csrf_token }}'
		},
		function(data) {
			if (null != data.status) {
				// Вывести сообщение
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
