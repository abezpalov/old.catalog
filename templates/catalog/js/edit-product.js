{% if perms.catalog.change_product %}


// Редактирование элемента
$("body").delegate("a[data-do*='edit-item']", "click", function(){

	// Заполняем значение полей модального окна
	$('#edit-item-id').val($(this).data('id'));
	$.post("/catalog/ajax/get-product/", {
		id: $('#edit-item-id').val(),
		csrfmiddlewaretoken: '{{ csrf_token }}'
	},
	function(data) {
		if (null != data.status) {
			if ('success' == data.status){
				$('#edit-item-name').val(data.product_name)
				$('#edit-item-article').val(data.product_article)
				$('#edit-item-vendor').val(data.product_vendor_id)
				$('#edit-item-category').val(data.product_category_id)
				$('#edit-item-description').val(data.product_description)
				$('#edit-item-double').val(data.product_duble_id)
				$('#edit-item-state').prop('checked', data.product_state)
			}
		}
	}, "json");

	// Открываем модальное окно
	$('#EditItemModal').foundation('reveal', 'open');
	return false;
});


// Сохранение элемента
$("body").delegate("button[data-do*='edit-item-save']", "click", function(){
	$.post("/catalog/ajax/save-product/", {
		id: $('#edit-item-id').val(),
		product_name: $('#edit-item-name').val(),
		product_article: $('#edit-item-article').val(),
		product_vendor_id: $('#edit-item-vendor').val(),
		product_category_id: $('#edit-item-category').val(),
		product_description: $('#edit-item-description').val(),
		product_duble_id: $('#edit-item-double').val(),
		product_state: $('#edit-item-state').prop('checked'),
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
{% endif %}
