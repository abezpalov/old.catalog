{% if perms.project.change_stock %}


// Открытие модального окна редактирования склада
$("body").delegate("[data-do*='open-edit-stock']", "click", function(){

	// Определяем значения переменных
	id                = $(this).data('id');
	name              = $(this).text();
	alias             = $(this).data('alias');
	state             = $('#stock-'+id+'-state').prop('checked');
	delivery_time_min = $('#stock-'+id+'-delivery-time-min').text();
	delivery_time_max = $('#stock-'+id+'-delivery-time-max').text();

	// Заполняем значение полей модального окна
	$('#edit-stock-id').val(id);
	$('#edit-stock-name').val(name);
	$('#edit-stock-alias').val(alias);
	$('#edit-stock-state').prop('checked', state);
	$('#edit-stock-delivery-time-min').val(delivery_time_min);
	$('#edit-stock-delivery-time-max').val(delivery_time_max);

	// Открываем модальное окно
	$('#EditStockModal').foundation('reveal', 'open');
	return false;
});


// Сохранение склада и закрытие модального окна
$("body").delegate("[data-do*='edit-stock-save']", "click", function(){

	// Определяем значения переменных
	id                = $('#edit-stock-id').val();
	name              = $('#edit-stock-name').val();
	alias             = $('#edit-stock-alias').val();
	state             = $('#edit-stock-state').prop('checked');
	delivery_time_min = $('#edit-stock-delivery-time-min').val();
	delivery_time_max = $('#edit-stock-delivery-time-max').val();

	// Отправляем AJAX-запрос
	$.post("/catalog/ajax/save-stock/", {
		id:                  id,
		name:                name,
		alias:               alias,
		state:               state,
		delivery_time_min:   $('#edit-stock-delivery-time-min').val(),
		delivery_time_max:   $('#edit-stock-delivery-time-max').val(),
		csrfmiddlewaretoken: '{{ csrf_token }}'
	},

	// Обрабатываем результат
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

	// Обновляем информацию в таблице
	$('#stock-'+id).data('alias', alias);
	$('#stock-'+id).text(name);
	$('#stock-'+id+'-state').prop('checked', state);
	$('#stock-'+id+'-delivery-time-min').text(delivery_time_min);
	$('#stock-'+id+'-delivery-time-max').text(delivery_time_max);

	// Закрываем модальное окно
	$('#EditStockModal').foundation('reveal', 'close');
	return false;
});


// Закрытие модального окна без сохранения изменений
$("body").delegate("[data-do*='edit-stock-cancel']", "click", function(){
	$('#EditStockModal').foundation('reveal', 'close');
	return false;
});

$("body").delegate("[data-do*='switch-stock-state']", "click", function(){
	$.post("/catalog/ajax/switch-stock-state/", {
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


{% endif %}
