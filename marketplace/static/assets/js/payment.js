const deliveryChoices = {
    regularru: 'Обычная доставка',
    expressru: 'Экспресс доставка',
    regularen: 'Regular shipping',
    expressen: 'Express delivery',
}

const paymentChoices = {
    onlineru: 'Онлайн картой',
    someoneru: 'Онлайн со случайного чужого счета',
    onlineen: 'Online payment by card',
    someoneen: 'Online payment from a random someone else\'s account',
}

const paymentStates = {
    'payedru': 'Оплачен',
    'not payedru': 'Не оплачен',
    'payeden': 'Paid up',
    'not payeden': 'Not paid'
}

function get_translated_value(source, key) {
    let lang = $('.language-option:selected').val()
    return source[$.trim(key) + $.trim(lang)]
}

function phone_mask() {
    var selector = document.querySelector("#phone");

    var im = new Inputmask("+7 (999) 999-99-99");
    im.mask(selector);
}

function handle_form_fields() {
    let fio;
    let phone;
    let mail;
    let password;
    let passwordReply;
    let delivery;
    let city;
    let address;
    let payment;

    $('#step2btn').on('click', function() {
        fio = $('#name').val()
        phone = $('#phone').val()
        mail = $('#mail').val()
        password = $('#phone').val()
        passwordReply = $('#passwordReply').val()
    })

    $('#step3btn').on('click', function() {
        city = $('#city').val()
        address = $('#address').val()
        delivery = $('input[name="delivery"]:checked').val()
    })

    $('#step4btn').on('click', function() {
        payment = $('input[name="pay"]:checked').val()
        $.ajax({
            url: '/ajax/get-order-cost',
            type: 'post',
            data:{
                "csrfmiddlewaretoken": $("input[name=csrfmiddlewaretoken]").val(),
                "delivery": delivery
            },
            success: function (response) {
                $('#total-price').text(response.total_price + '$')
            }
            });
        $('#fio-confirm').text(fio)
        $('#phone-confirm').text(phone)
        $('#mail-confirm').text(mail)
        $('#city-confirm').text(city)
        $('#address-confirm').text(address)
        $('#delivery-confirm').text(get_translated_value(deliveryChoices, delivery))
        $('#payment-confirm').text(get_translated_value(paymentChoices, payment))
    })
}

function handle_payment_request(server_url, card) {
    $.ajax({
        url: server_url + '/pay',
        type: 'post',
        data: {
            "card": card
        },
        crossDomain: true,
        success: function(response) {
            resp_obj = $.parseJSON(response)
            window.location.replace("/payment/success/" + resp_obj['token']);
        },
        error: function() {
            window.location.replace("/payment/error");
        },
    })
}

function rewrite_fields() {
    $('.Order-infoContent').each(function() {
        let value = $(this).text()
        key = $.trim(value) + $.trim($('.language-option:selected').val())
        if (key in deliveryChoices) {
            $(this).text(deliveryChoices[key])
        } else if (key in paymentChoices) {
            $(this).text(paymentChoices[key])
        } else if (key in paymentStates) {
            $(this).text(paymentStates[key])
        }
    })
}
