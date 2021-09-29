var Amount = function(){
    var $amount = $('.Amount');
    var $add = $('.Amount-add');
    var $input = $('.Amount-input');
    var $remove = $('.Amount-remove');
    return {
        init: function(){
            $add.on('click', function(e){
                e.preventDefault();
                var $inputThis = $(this).siblings($input).filter($input);
                var value = parseFloat($inputThis.val());
                $inputThis.val( value + 1);
                let warehouseId = $inputThis.attr('data-warehouse-id')
                $(".Cart-accept-message[data-warehouse-id=" + warehouseId+ "]").text("")
            });
            $remove.on('click', function(e){
                e.preventDefault();
                var $inputThis = $(this).siblings($input).filter($input);
                var value = parseFloat($inputThis.val());
                $inputThis.val(value>0?value - 1:0);
                let warehouseId = $inputThis.attr('data-warehouse-id')
                $(".Cart-accept-message[data-warehouse-id=" + warehouseId+ "]").text("")
            });
        }
    };
};

function handle_modal(){
    $('.Cart-add').click(function(e) {
        e.preventDefault();
        let $this = $(this)
        let productId = $this.attr('data-product-id')
        let div_modal = $("#modal")
        var winH = $(window).height();
        var winW = $(window).width();
        //Устанавливаем всплывающее окно по центру
        div_modal.css('top', winH/7);
        div_modal.css('left', winW/2-div_modal.width()/2);

        $.ajax({
        url: '/ajax/get-warehouses-modal-content',
        type: 'get',
        data:{
            "product_id": productId
        },
        success: function (response) {
            $(".modal__content").html(response.modal_content)
            $(".modalwindow h2").text(response.modal_header_text)
            Amount().init();  // TODO вызвать из изначальных скриптов
            handle_add_to_cart()
            $(".btn__add-to-cart").attr("data-product-id", productId)
        },
        });
        //эффект перехода
        div_modal.fadeIn(500);
    });
    //если нажата кнопка закрытия окна
    $('.modalwindow .close').click(function (e) {
        e.preventDefault();
        $('.modalwindow').fadeOut(500);
    });
    //Если клик мимо модального окна, то скрываем модальное окно
    $('body').mouseup(function (e) {
       let modalContent = $(".modalwindow");
       if (!modalContent.is(e.target) && modalContent.has(e.target).length === 0) {
           $('.modalwindow').fadeOut(500);
       }
    });
    // если нажат ESC то убираем модальное окно
    $(document).on('keydown', function(e) {
        if (e.which === 27) { // key = esc (27)
            $('.modalwindow').fadeOut(500);
            return false;
        }
    })
}

function handle_add_to_cart(){
    $(".btn__add-to-cart").click(function (e){
        e.preventDefault();
        let $this = $(this)
        let warehouseId = $this.attr('data-warehouse-id')
        let amount = $(".Amount-input[data-warehouse-id=" + warehouseId + "]").val()
        let productId = $(".btn__add-to-cart").attr("data-product-id")
        $.ajax({
        url: '/ajax/add-to-cart',
        type: 'post',
        data:{
            "csrfmiddlewaretoken": $("input[name=csrfmiddlewaretoken]").val(),
            "product_id": productId,
            "amount": amount,
            "warehouse_id": warehouseId
        },
        success: function (response) {
            let messageSpan = $(".Cart-accept-message[data-warehouse-id=" + warehouseId + "]")
            messageSpan.text(response.message)
            if (response.success){
                messageSpan.css("color", 'green')
                $(".Stock-balance[data-warehouse-id=" + warehouseId+ "]").text(response.new_stock_balance)
                refresh_cart_info()
            }else{
                messageSpan.css("color", 'red')
            }
        },
        })
    })
}