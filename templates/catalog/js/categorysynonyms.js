$(document).ready(function(){

	$("body").delegate(".do-filter-table", "change", function(){
		location.href = "/catalog/category-synonyms/" + $("#filter-updater").val() + "/" + $("#filter-distributor").val() + "/" + $("#filter-category").val() + "/";
		return true;
	});

	$("body").delegate("a[data-do*='edit-item']", "click", function(){

		// Заполняем значение полей модального окна
		$('#edit-item-id').val($(this).data('id'));
		$('#edit-item-category').val($(this).data('category'));
		$('#edit-item-name').val($(this).text());

		// Открываем модальное окно
		$('#EditItemModal').foundation('reveal', 'open');
		return false;
	});

	$("body").delegate("button[data-do*='edit-item-save']", "click", function(){
		$.post("/catalog/ajax/link-category-synonym/", {
			synonym: $('#edit-item-id').val(),
			category: $('#edit-item-category').val(),
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
		$('#item-'+$('#edit-item-id').val()).text($('#edit-item-name').val());
		$('#EditItemModal').foundation('reveal', 'close');
		return false;
	});

	$("body").delegate("button[data-do*='edit-item-cancel']", "click", function(){
		$('#EditItemModal').foundation('reveal', 'close');
		return false;
	});


	$("body").delegate("button[data-do*='trash-item']", "click", function(){
		$.post("/catalog/ajax/trash-category-synonym/", {
			id: $(this).data('id'),
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
