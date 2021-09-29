function refresh_cart_cost(){
    // Функция для обновления информации о стоимости корзины в шапке сайта

    $.ajax({
        url: '/ajax/get-cart-cost',
        type: 'get',
        data: {},
        success: function (response) {
            $(".CartBlock-price").text(response.cart_cost + ',0$')
        },
    });
}

function refresh_cart_size(){
    // Функция для обновления информации о количестве товаров в корзине в шапке сайта

    $.ajax({
        url: '/ajax/get-cart-size',
        type: 'get',
        data: {},
        success: function (response) {
            $(".Cart-size").text(response.cart_size)
        },
    });
}

function refresh_cart_info(){
    // Функция для обновления информации о корзине в шапке сайта: количество и стоимость
    refresh_cart_cost()
    refresh_cart_size()
}