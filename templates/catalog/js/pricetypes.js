$(document).ready(function(){

	$("body").delegate("input[data-do*='switch-item-state']", "click", function(){
		$.post("/catalog/ajax/switch-price-type-state/", {
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
		$('#edit-item-multiplier').val($(this).data('multiplier'));

		// Открываем модальное окно
		$('#EditItemModal').foundation('reveal', 'open');

		return false;
	});

	$("body").delegate("button[data-do*='edit-item-save']", "click", function(){
		$.post("/catalog/ajax/save-price-type/", {
			id: $('#edit-item-id').val(),
			name: $('#edit-item-name').val(),
			alias: $('#edit-item-alias').val(),
			multiplier: $('#edit-item-multiplier').val(),
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
		$('#price-type-'+$('#edit-item-id').val()).data('alias', $('#edit-item-alias').val());
		$('#price-type-'+$('#edit-item-id').val()).text($('#edit-item-name').val());
		$('#price-type-'+$('#edit-item-id').val()).data('multiplier', $('#edit-item-multiplier').val());
		$('#price-type-multiplier-'+$('#edit-item-id').val()).text($('#edit-item-multiplier').val());
		$('#EditItemModal').foundation('reveal', 'close');
		return false;
	});

	$("body").delegate("button[data-do*='edit-item-cancel']", "click", function(){
		$('#EditItemModal').foundation('reveal', 'close');

		return false;
	});
});
