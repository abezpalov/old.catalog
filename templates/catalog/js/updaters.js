$(document).ready(function(){

	$("body").delegate(".do-switch-item-state", "click", function(){
		$.post("/catalog/ajax/switch-updater-state/", {
			id: $(this).data('id'),
			state: $(this).prop("checked"),
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

	$("body").delegate("a[data-do*='edit-item']", "click", function(){

		// Заполняем значение полей модального окна
		$('#edit-item-id').val($(this).data('id'));
		$('#edit-item-alias').val($(this).data('alias'));
		$('#edit-item-name').val($(this).text());
		$('#edit-item-login').val($(this).data('login'));
		$('#edit-item-password').val($(this).data('password'));

		// Открываем модальное окно
		$('#EditItemModal').foundation('reveal', 'open');
		return false;
	});


	$("body").delegate("button[data-do*='edit-item-save']", "click", function(){
		$.post("/catalog/ajax/save-updater/", {
			id: $('#edit-item-id').val(),
			name: $('#edit-item-name').val(),
			alias: $('#edit-item-alias').val(),
			login: $('#edit-item-login').val(),
			password: $('#edit-item-password').val(),
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
		$('#updater-'+$('#edit-item-id').val()).data('alias', $('#edit-item-alias').val());
		$('#updater-'+$('#edit-item-id').val()).text($('#edit-item-name').val());
		$('#updater-'+$('#edit-item-id').val()).data('login', $('#edit-item-login').val());
		$('#updater-'+$('#edit-item-id').val()).data('password', $('#edit-item-password').val());
		$('#EditItemModal').foundation('reveal', 'close');
		return false;
	});

	$("body").delegate("button[data-do*='edit-item-cancel']", "click", function(){
		$('#EditItemModal').foundation('reveal', 'close');
		return false;
	});
});
