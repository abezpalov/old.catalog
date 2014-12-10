$(document).ready(function(){


	$("body").delegate(".do-filter-table", "change", function(){
		location.href = "/catalog/vendor-synonyms/" + $("#filter-updater").val() + "/" + $("#filter-distributor").val() + "/" + $("#filter-vendor").val() + "/";
		return true;
	});


	$("table").delegate(".do-link-vendor-synonym", "change", function(){
		$.post("/catalog/ajax/link-vendor-synonym/", {
			synonym: $(this).data('id'),
			vendor: $(this).val(),
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


	$("body").delegate(".do-link-vendor-same-synonym", "click", function(){
		$.post("/catalog/ajax/link-vendor-same-synonym/", {
			synonym: $(this).data('id'),
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
				setTimeout(function () {location.reload();}, 3000);
			}
		}, "json");
		return false;
	});
});
