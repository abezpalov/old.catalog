{% if perms.catalog.add_vendorkey or perms.catalog.change_vendorkey or perms.catalog.delete_vendorkey %}
$("body").delegate("[data-do='filter-vendorkeys']", "change", function(){
	location.href = "/catalog/vendorkeys/" + $("#filter-updater").val() + "/" + $("#filter-vendor").val() + "/";
	return true;
});
{% endif %}


{% if perms.catalog.add_vendorkey %}
$("body").delegate("[data-do='open-new-vendorkey']", "click", function(){

	model = 'vendorkey';

	$('#modal-edit-' + model + '-header').text('Добавить синоним производителя');

	$('#edit-' + model + '-id').val('0');
	$('#edit-' + model + '-name').val('');
	$('#edit-' + model + '-updater').val('0');
	$('#edit-' + model + '-vendor').val('0');

	$('#modal-edit-' + model).foundation('reveal', 'open');

	return false;
});
{% endif %}


{% if perms.catalog.change_vendorkey %}
$("body").delegate("[data-do='open-edit-vendorkey']", "click", function(){

	model = 'vendorkey';

	$.post('/catalog/ajax/get/' + model + '/', {
		id : $(this).data(model + '-id'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {
		if ('success' == data.status){

			$('#modal-edit-' + model + '-header').text('Редактировать синоним производителя');

			$('#edit-' + model + '-id').val(data[model]['id']);
			$('#edit-' + model + '-name').val(data[model]['name'])
			if (data[model]['updater']) {
				$('#edit-' + model + '-updater').val(data[model]['updater']['id']);
			} else {
				$('#edit-' + model + '-updater').val(0);
			}
			if (data[model]['vendor']) {
				$('#edit-' + model + '-vendor').val(data[model]['vendor']['id']);
			} else {
				$('#edit-' + model + '-vendor').val(0);
			}

			$('#modal-edit-' + model).foundation('reveal', 'open');
		}
	}, "json");
	return false;
});
{% endif %}


{% if perms.catalog.change_vendorkey %}
$("body").delegate("[data-do='edit-vendorkey-save']", "click", function(){

	model = 'vendorkey';

	$.post('/catalog/ajax/save/' + model + '/', {
		id             : $('#edit-' + model + '-id').val(),
		name           : $('#edit-' + model + '-name').val(),
		updater_id     : $('#edit-' + model + '-updater').val(),
		vendor_id      : $('#edit-' + model + '-vendor').val(),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {

		if ('success' == data.status){

			$('[data-' + model + '-name="' + data[model]['id'] + '"]').text(data[model]['name']);

			if (data[model]['updater']) {
				$('[data-' + model + '-updater-name="' + data[model]['id'] + '"]').text(data[model]['updater']['name']);
				$('[data-' + model + '-updater-name="' + data[model]['id'] + '"]').data('updater-id', data[model]['updater']['id']);
				$('[data-' + model + '-updater-name="' + data[model]['id'] + '"]').data('updater-name', data[model]['updater']['id']);
			} else {
				$('[data-' + model + '-updater-name="' + data[model]['id'] + '"]').text('');
				$('[data-' + model + '-updater-name="' + data[model]['id'] + '"]').data('updater-id', '0');
				$('[data-' + model + '-updater-name="' + data[model]['id'] + '"]').data('updater-name', '0');
			}

			if (data[model]['vendor']) {
				$('[data-' + model + '-vendor-name="' + data[model]['id'] + '"]').text(data[model]['vendor']['name']);
				$('[data-' + model + '-vendor-name="' + data[model]['id'] + '"]').data('vendor-id', data[model]['vendor']['id']);
				$('[data-' + model + '-vendor-name="' + data[model]['id'] + '"]').data('vendor-name', data[model]['vendor']['id']);
			} else {
				$('[data-' + model + '-vendor-name="' + data[model]['id'] + '"]').text('');
				$('[data-' + model + '-vendor-name="' + data[model]['id'] + '"]').data('vendor-id', '0');
				$('[data-' + model + '-vendor-name="' + data[model]['id'] + '"]').data('vendor-name', '0');
			}

			$('#edit-' + model + '-id').val('0');
			$('#edit-' + model + '-name').val('');
			$('#edit-' + model + '-updater').val('0');
			$('#edit-' + model + '-distributor').val('0');
			$('#edit-' + model + '-vendor').val('0');

			$('#modal-edit-' + model).foundation('reveal', 'close');
		}
	}, "json");

	return false;
});
{% endif %}


{% if perms.catalog.change_vendorkey %}
$("body").delegate("[data-do='edit-vendorkey-cancel']", "click", function(){

	model = 'vendorkey';


	$('#edit-' + model + '-id').val('0');
	$('#edit-' + model + '-name').val('');
	$('#edit-' + model + '-updater').val('0');
	$('#edit-' + model + '-category').val('0');

	$('#modal-edit-' + model).foundation('reveal', 'close');

	return false;
});
{% endif %}


{% if perms.catalog.delete_vendorkey %}
$("body").delegate("[data-do='open-delete-vendorkey']", "click", function(){

	model = 'vendorkey';

	$.post('/catalog/ajax/get/' + model + '/', {
		id : $(this).data(model + '-id'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {
		if ('success' == data.status){

			$('#delete-' + model + '-id').val(data[model]['id']);
			$('#delete-' + model + '-name').text(data[model]['name'])

			$('#modal-delete-' + model).foundation('reveal', 'open');
		}
	}, "json");

	return false;
});
{% endif %}


{% if perms.catalog.delete_vendorkey %}
$("body").delegate("[data-do='delete-vendorkey-apply']", "click", function(){

	model = 'vendorkey';

	$.post('/catalog/ajax/delete/' + model + '/', {
		id : $('#delete-' + model + '-id').val(),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {
		if ('success' == data.status) {

			$('[data-' + model + '="' + data['id'] + '"]').empty();

			$('#modal-delete-' + model).foundation('reveal', 'close');
		}
	}, "json");

	return false;
});
{% endif %}


{% if perms.catalog.delete_vendorkey %}
$("body").delegate("[data-do='delete-vendorkey-cancel']", "click", function(){

	model = 'vendorkey';

	$('#delete-' + model + '-id').val(0);

	$('#modal-delete-' + model).foundation('reveal', 'close');

	return false;
});
{% endif %}


{% if perms.catalog.change_vendorkey %}
$("body").delegate("[data-do='link-vendorkey-same-vendor']", "click", function(){

	model = 'vendorkey';
	foreign = 'vendor';

	$.post('/catalog/ajax/link/' + model + '/same/' + foreign + '/', {
		id : $(this).data(model + '-id'),
		csrfmiddlewaretoken : '{{ csrf_token }}'
	},
	function(data) {
		if ('success' == data.status) {

			$('[data-' + model + '-' + foreign + '-name="' + data[model]['id'] + '"]').text(data[model][foreign]['name']);
			$('[data-' + model + '-' + foreign + '-name="' + data[model]['id'] + '"]').data(foreign + '-id', data[model][foreign]['id']);
			$('[data-' + model + '-' + foreign + '-name="' + data[model]['id'] + '"]').data(foreign + '-name', data[model][foreign]['id']);

			// TODO Обновляем список производителей в окне редактирования синонимов
		}
	}, "json");
	return false;
});
{% endif %}
