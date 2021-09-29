function handle_delete_cartline(){
    // функция для обработки нажатия кнопки удаления позиции корзины

    $(".Cartline-delete").click(function (b) {
            b.preventDefault();
            let $this = $(this)
            let cartLineId = $this.attr('data-line')
            $.ajax({
            url: '/ajax/delete-cartline',
            type: 'post',
            data:{
                "csrfmiddlewaretoken": $("input[name=csrfmiddlewaretoken]").val(),
                "cartline_id": cartLineId
            },
            success: function (response) {
                delete_cartline_div(cartLineId)
            }
            });
        });
}

function refresh_cart_content(){
    // Функция для обновления корзины, если не осталось позиций,
    // то выводится сообощение о пустоте корзины в зависимости от выбранного языка
    if ($(".Cart-product").length == 0){
        $.ajax({
            url: '/ajax/get-empty-cart-message',
            type: 'get',
            data: {},
            success: function (response){
                $(".wrap-main").html('<p>' + response.message + '</p>')
            }
        })

    }
}

function refresh_page_cart_cost(){
    // функция для обновления стоимости корзины на странице корзины

    $.ajax({
        url: '/ajax/get-cart',
        type: 'get',
        data:{},
        success: function (response) {
            let discountCartCost = response.discount_cost
            let oldCartCost = response.old_cost
            if (discountCartCost == oldCartCost){
                $(".Cart-cost-total").html("<span class=\"Cart-price Cart-total-cost\">" +
                    discountCartCost +"$</span>")
            }else{
                $(".Cart-cost-total").html("<span class=\"Cart-price Cart-total-cost\">" +
                    discountCartCost + "$</span>" +
                    "<span class=\"Cart-price_old\">" + oldCartCost + "$</span>")
            }
        },
    });
}

function handle_clear_cart(){
    // Функция для очистки корзины
    $(".Cart-clear").click(function (b) {
        b.preventDefault();
        $.ajax({
            url: '/ajax/clear-cart',
            type: 'post',
            data:{
                "csrfmiddlewaretoken": $("input[name=csrfmiddlewaretoken]").val()
            },
            success: function (response) {
                $('html, body').animate({scrollTop: '50px'}, 300);
                $('.Cart-product:eq(0)').hide("slow", function () {
                    $(this).next().hide("slow", arguments.callee);
                    $(this).remove()
                    refresh_cart_content()
                 });
                refresh_cart_info()
            }
        });
    });
}

function delete_cartline_div(cartLineId){
    // функция для удаления позиции корзины по id объекта CartLIne
    let cartLineDiv = $(".Cart-product[data-line='" + cartLineId +"']")
    cartLineDiv.hide(1000, function () {
        cartLineDiv.remove();
        refresh_cart_info()
        refresh_page_cart_cost()
        refresh_cart_content()
    });
}

function handle_accept_amount(){
    // Функция для обработки нажатия на кнопку применения изменний количества

    $(".Cart-accept").click(function (b) {
        b.preventDefault();
        let $this = $(this)
        let cartLineId = $this.attr('data-line')
        let new_quantity = $(".Amount-input[data-line=" + cartLineId+ "]").val()
        $.ajax({
        url: '/ajax/change-cartline-quantity',
        type: 'post',
        data:{
            "csrfmiddlewaretoken": $("input[name=csrfmiddlewaretoken]").val(),
            "cartline_id": cartLineId,
            "new_quantity": new_quantity
        },
        success: function (response) {
            if (new_quantity == 0){
                delete_cartline_div(cartLineId)
                return
            }
            let messageSpan = $(".Cart-accept-message[data-line=" + cartLineId+ "]")
            messageSpan.text(response.message)
            if (response.success){
                messageSpan.css("color", 'green')
                $(".Stock-balance[data-line=" + cartLineId+ "]").text(response.new_stock_balance)
            }else{
                messageSpan.css("color", 'red')
            }
            refresh_cart_info()
            refresh_page_cart_cost()
        }
        });
    });
}