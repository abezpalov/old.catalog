$("body").delegate("[data-do='open-product']", "click", function(){

    $.post('/catalog/ajax/get/product/', {
        id: $(this).data('product-id'),
        csrfmiddlewaretoken: '{{ csrf_token }}'
    },
    function(data) {
        if ('success' == data.status){

            // Заполняем базовую информацию о товаре
            if (data['product']['vendor']) {
                $('#modal-product-header').text(
                    data['product']['vendor']['name'] + ' ' + data['product']['article'])
            } else {
                $('#modal-product-header').text('');
            }
            $('#view-product-name').text(data['product']['name']);
            $('#view-product-description').text(data['product']['description']);

            // Заполняем информацию по партиям
            if (0 < data.product.parties.length) {
                {% if perms.catalog.change_price %}
                thead = "<tr><th>Склад</th><th>Срок поставки</th><th>Количество</th><th>Цена<br/>(вход)</th><th>Цена<br/>(выход)</th></tr>"
                tbody = ""
                for(i = 0; i < data.product.parties.length; i++) {
                    tr = "<tr><td>" + data.product.parties[i]['stock']['name'] + "</td><td>" + data.product.parties[i]['stock']['delivery_time_min'] + "&ndash;" + data.product.parties[i]['stock']['delivery_time_max'] + "&nbsp;дней</td><td>" + data.product.parties[i]['quantity'] + "</td><td>" + data.product.parties[i]['price_xml'] + "</td><td>" + data.product.parties[i]['price_out_xml'] + "</td></tr>";
                    tbody = tbody + tr;
                }
                {% else %}
                thead = "<tr><th>Срок поставки</th><th>Количество</th><th>Цена</th></tr>"
                tbody = ""
                for(i = 0; i < data.product.parties.length; i++) {
                    tr = "<tr><td>" + data.product.parties[i]['stock']['delivery_time_min'] + "&ndash;" + data.product.parties[i]['stock']['delivery_time_max'] + "&nbsp;дней</td><td>" + data.product.parties[i]['quantity'] + "</td><td>" + data.product.parties[i]['price_out_xml'] + "</td></tr>";
                    tbody = tbody + tr;
                }
                {% endif %}
                html_data = '<table class="ui basic table"><thead>' + thead + "</thead><tbody>" + tbody + "</tbody></table>";
            } else {
                html_data = 'Товар отсутствует.';
            }
            $('#view-product-parties').html(html_data);

            {% if perms.catalog.change_product %}
            // Заполняем форму редактирования товара
            $('#edit-product-id').val(data['product']['id']);
            $('#edit-product-name').val(data['product']['name']);
            $('#edit-product-article').val(data['product']['article']);
            if (data['product']['vendor']) {
                $('#edit-product-vendor').val(data['product']['vendor']['id']);
            } else {
                $('#edit-product-vendor').val(0);
            }
            if (data['product']['category']) {
                $('#edit-product-category').val(data['product']['category']['id']);
            } else {
                $('#edit-product-category').val(0);
            }
            $('#edit-product-description').val(data['product']['description']);
            if (data['product']['double']) {
                $('#edit-product-double').val(data['product']['double']['id']);
            } else {
                $('#edit-product-double').val(0);
            }
            $('#edit-product-state').prop('checked', data['product']['state']);
            {% endif %}

            // Отображаем модальное окно
            $('#modal-product').modal('show');
        }
    }, "json");
    return false;
});

{% if perms.catalog.change_product %}
$("body").delegate("[data-do='edit-product-save']", "click", function(){

    $.post('/catalog/ajax/save/product/', {
        id: $('#edit-product-id').val(),
        name: $('#edit-product-name').val(),
        article: $('#edit-product-article').val(),
        vendor_id: $('#edit-product-vendor').val(),
        category_id: $('#edit-product-category').val(),
        description: $('#edit-product-description').val(),
        duble_id: $('#edit-product-double').val(),
        state: $('#edit-product-state').prop('checked'),
        csrfmiddlewaretoken: '{{ csrf_token }}'
    },
    function(data) {

        if ('success' == data.status){

            $('[data-product-name="' + data['product']['id'] + '"]').text(data['product']['name']);
            $('[data-product-article="' + data['product']['id'] + '"]').text(data['product']['article']);
            $('[data-product-state="' + data['product']['id'] + '"]').prop('checked', data['product']['state']);
            result = true;
            if (true == data.reload){
                setTimeout(function () {location.reload();}, 3000);
            }
        } else {
            result = false;
    }, "json");
    return result;
});
{% endif %}

{% if perms.catalog.change_product %}
$("body").delegate("[data-do='switch-product-state']", "click", function(){

    $.post('/catalog/ajax/switch-state/product/', {
        id: $(this).data('product-id'),
        state: $(this).prop('checked'),
        csrfmiddlewaretoken: '{{ csrf_token }}'
    },
    function(data) {
        if ('success' == data.status) {
            result = false;
        } else {
            result = true;
        }
    }, "json");
    return result;
});
{% endif %}
