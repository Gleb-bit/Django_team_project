// JS для добавления к фильтрам по сбросу кешей checkbox'а для выбора/ снятия выбора сброса всех кешей

function add_all_caches_reset_input(){
    // Функция добавления checkbox c #reset_all  "Выбрать всё / снять выбор" для сброса кешей.

    $("#h3_caches_reset").after("<p><label for='reset_all' style='margin-right: 5px;'>Select all / deselect: </label>" +
        "<input type='checkbox' id='reset_all'></p>")
    $("#reset_all").change(set_reset_caches);
    $(".caches-delete__container p input.caches-delete").change(set_reset_all)
    set_reset_all()
}

function set_reset_caches(){
    // функция для выбора/снятия выбора всех чекбоксов для сброса кешей в зависимости от чекбокса #reset_all

    let reset_all_caches = $("#reset_all").prop('checked');
    if (reset_all_caches) {
        $(".caches-delete__container p input.caches-delete").prop("checked",true);
    }
    else {
        $(".caches-delete__container p input.caches-delete").prop("checked",false);
    }
}

function set_reset_all(){
    // функция для установления чекбокса #reset_all в зависимости от выбранности остальных  чекбоксом по сбросу кешей

    let checked = [];
    $('.caches-delete__container p input.caches-delete').each(function() {
        checked.push($(this).prop("checked"));
    });
    let is_all_reset_caches_checked = checked.every(elem => (elem))
    if (is_all_reset_caches_checked){
        $("#reset_all").prop("checked",true);
    }
    else{
        $("#reset_all").prop("checked",false);
    }
}
