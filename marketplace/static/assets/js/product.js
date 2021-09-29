// Доп JS для детальной страницы товара

$(document).ready(function () {
    // показ блока #sellers если в ссылке есть якорь на этот блок
    if(document.location.hash == "#sellers"){
        show_sellers()
        $('#sellers').scroll()
    }
});

function show_sellers(){
    // функция для показа блока с продацами

    $('.Tabs-block').hide()  // скрываем все блоки
    $('.Tabs-link').removeClass('Tabs-link_ACTIVE') // удаляем класс выделения для всех ссылок

    $('#sellers').show() // отображаем блок с продавцами
    $('.Tabs-link[href="#sellers"]').addClass('Tabs-link_ACTIVE') // выделение ссылки на блок продавцов
}