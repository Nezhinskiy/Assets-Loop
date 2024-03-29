function roundToTwo(num) {
  if (Number.isInteger(num) || num.toFixed(1) === num) {
    return num;
  }
  if (num.toFixed(2) !== num) {
    return +num.toFixed(2);
  }
  return num;
}

function updateTime(updated) {
    let seconds = Math.ceil((new Date() - new Date(updated)) / 1000);
    return seconds > 999 ? 999 : seconds;
}

function colorSelector(marginality_percentage) {
    return marginality_percentage > 0 ? 'green' : 'red';
}

function bankExchange(row, bank) {
    if (!row.bank_exchange.currency_market) {
        return `внутри банка ${bank} нужно поменять 
        ${row.bank_exchange.from_fiat} на ${row.bank_exchange.to_fiat} 
        по курсу ${row.bank_exchange.price}, с учётом комиссии.`;
    } else {
        return `внутри банка ${bank} нужно поменять 
        ${row.bank_exchange.from_fiat} на ${row.bank_exchange.to_fiat} 
        через биржу ${row.bank_exchange.currency_market.name}, по курсу 
        ${row.bank_exchange.price}, с учётом комиссии.`;
    }
}

function inputP2P(row) {
    return `со счёта ${row.input_bank.name} нужно купить активы на криптобирже 
    ${row.crypto_exchange.name}. За 
    ${row.input_crypto_exchange.fiat} следует купить 
    ${row.input_crypto_exchange.asset} методом P2P по курсу 
    ${row.input_crypto_exchange.price}. P2P не облагается комиссией.`;
}

function inputCard2CryptoExchange(row) {
    return `со счёта ${row.input_bank.name} нужно купить активы на криптобирже 
    ${row.crypto_exchange.name}. За 
    ${row.input_crypto_exchange.fiat} следует купить 
    ${row.input_crypto_exchange.asset} методом 
    Card2CryptoExchange через ${row.input_crypto_exchange.transaction_method}, 
    по курсу ${row.input_crypto_exchange.price}. В стоимость включена комиссия 
    биржи ${roundToTwo(row.input_crypto_exchange.transaction_fee)}%.`;
}

function inputCard2Wallet2CryptoExchange(row) {
    return `со счёта ${row.input_bank.name} нужно купить активы на криптобирже 
    ${row.crypto_exchange.name}. За 
    ${row.input_crypto_exchange.fiat} следует купить 
    ${row.input_crypto_exchange.asset} методом 
    Card2Wallet2CryptoExchange по итоговому курсу с учётом всех комиссий - 
    ${row.input_crypto_exchange.price}. Этот метод состоит из двух транзакций: 
    1. Нужно перевести ${row.input_crypto_exchange.fiat} на свой 
    ${row.crypto_exchange.name} кошелёк через 
    ${row.input_crypto_exchange.transaction_method}. Комиссия составит 
    ${roundToTwo(row.input_crypto_exchange.transaction_fee)}%. 
    2. Далее, уже внутри биржи надо конвертировать через Спот 
    ${row.input_crypto_exchange.fiat} в ${row.input_crypto_exchange.asset} 
    по курсу ${row.input_crypto_exchange.intra_crypto_exchange.price} c учётом 
    комиссии ${row.input_crypto_exchange.intra_crypto_exchange.spot_fee}%.`;
}

function inputCryptoExchange(row) {
    if (row.input_crypto_exchange.payment_channel === 'P2P') {
        return inputP2P(row);
    }
    if (row.input_crypto_exchange.payment_channel === 'Card2CryptoExchange') {
        return inputCard2CryptoExchange(row);
    }
    if (row.input_crypto_exchange.payment_channel === 'Card2Wallet2CryptoExchange') {
        return inputCard2Wallet2CryptoExchange(row);
    }
    return row.input_crypto_exchange.payment_channel
}

function interimCryptoExchange(row) {
    if (row.second_interim_crypto_exchange) {
        return `Теперь внутри ${row.crypto_exchange.name} через Спот надо 
        сначала конвертировать ${row.interim_crypto_exchange.from_asset} в 
        ${row.interim_crypto_exchange.to_asset} по курсу 
        ${row.interim_crypto_exchange.price} (комиссия биржи 
        ${row.interim_crypto_exchange.spot_fee}%), а потом 
        ${row.interim_crypto_exchange.to_asset} в 
        ${row.second_interim_crypto_exchange.to_asset} по курсу 
        ${row.second_interim_crypto_exchange.price} (комиссия биржи
        ${row.second_interim_crypto_exchange.spot_fee}%). Все комиссии 
        включены в стоимость.`;
    } else {
        return `Теперь внутри ${row.crypto_exchange.name} через Спот надо 
        конвертировать ${row.interim_crypto_exchange.from_asset} в 
        ${row.interim_crypto_exchange.to_asset} по курсу 
        ${row.interim_crypto_exchange.price}. Комиссия биржи 
        ${row.interim_crypto_exchange.spot_fee}% включена в стоимость.`;
    }
}

function outputP2P(row) {
    return `нужно перевести активы с ${row.crypto_exchange.name} на счёт 
    ${row.output_bank.name} по методу 
    ${row.output_crypto_exchange.payment_channel}. Перевести 
    ${row.output_crypto_exchange.asset} в ${row.output_crypto_exchange.fiat} 
    по курсу ${row.output_crypto_exchange.price}. P2P не облагается 
    комиссией.`;
}

function outputCard2CryptoExchange(row) {
    return `нужно перевести активы с ${row.crypto_exchange.name} на счёт 
    ${row.output_bank.name} по методу CryptoExchange2Card через 
    ${row.output_crypto_exchange.transaction_method}. Перевести 
    ${row.output_crypto_exchange.asset} в ${row.output_crypto_exchange.fiat} 
    по курсу ${row.output_crypto_exchange.price}.  В стоимость включена 
    комиссия биржи 
    ${roundToTwo(row.output_crypto_exchange.transaction_fee)}%.`;
}

function outputCard2Wallet2CryptoExchange(row) {
    return `нужно перевести активы с ${row.crypto_exchange.name} на счёт 
    ${row.output_bank.name} по методу CryptoExchange2Wallet2Card. Перевести 
    ${row.output_crypto_exchange.asset} в ${row.output_crypto_exchange.fiat} 
    по итоговому курсу ${row.output_crypto_exchange.price} с учётом всех 
    комиссий. Этот метод состоит из двух транзакций: 1. Нужно внутри биржи 
    через Спот конвертировать ${row.output_crypto_exchange.asset} в 
    ${row.output_crypto_exchange.fiat} 
    на свой ${row.crypto_exchange.name} кошелёк, по курсу 
    ${row.output_crypto_exchange.intra_crypto_exchange.price} c учётом 
    комиссии ${row.output_crypto_exchange.intra_crypto_exchange.spot_fee}%. 
    2. Далее, нужно вывести с ${row.crypto_exchange.name} кошелька 
    ${row.output_crypto_exchange.fiat} на свой ${row.output_bank.name} счёт 
    через ${row.output_crypto_exchange.transaction_method}. Комиссия составит 
    ${roundToTwo(row.output_crypto_exchange.transaction_fee)}%.`;
}

function outputCryptoExchange(row) {
    if (row.output_crypto_exchange.payment_channel === 'P2P') {
        return outputP2P(row);
    }
    if (row.output_crypto_exchange.payment_channel === 'Card2CryptoExchange') {
        return outputCard2CryptoExchange(row);
    }
    if (row.output_crypto_exchange.payment_channel === 'Card2Wallet2CryptoExchange') {
        return outputCard2Wallet2CryptoExchange(row);
    }
    return row.output_crypto_exchange.payment_channel
}

function modalWrite(row) {
    let modal = ''
    if (row.bank_exchange && row.bank_exchange.bank.name === row.input_bank.name) {
        modal += `<p>1. Сначала ${bankExchange(row, row.input_bank.name)}</p><p>2. Далее, ${inputCryptoExchange(row)}</p>`
        if (row.interim_crypto_exchange) {
            modal += `<p>3. ${interimCryptoExchange(row)}</p><p>4. Последнее, ${outputCryptoExchange(row)}</p>`
        } else {
            modal += `<p>3. Последнее, ${outputCryptoExchange(row)}</p>`
        }
    } else {
        modal += `<p>1. Сначала ${inputCryptoExchange(row)}</p>`
        if (row.interim_crypto_exchange) {
            modal += `<p>2. ${interimCryptoExchange(row)}</p>`
            if (!row.bank_exchange) {
                modal += `<p>3. Последнее, ${outputCryptoExchange(row)}</p>`
            } else {
                modal += `<p>3. Далее, ${outputCryptoExchange(row)}</p><p>4. Последнее, ${bankExchange(row, row.output_bank.name)}</p>`
            }
        } else {
            if (!row.bank_exchange) {
                modal += `<p>2. Последнее, ${outputCryptoExchange(row)}</p>`
            } else {
                modal += `<p>2. Далее, ${outputCryptoExchange(row)}</p><p>3. Последнее, ${bankExchange(row, row.output_bank.name)}</p>`
            }
        }
    }
    return modal;
}

$(document).ready(function () {
    var refreshTable = $('#dynamicDatatable').DataTable({
        "language": dt_language,
        "searching": false,
        "pageLength": 10,
        "lengthMenu": [[10, 25, 50, 100], [10, 25, 50, 100]],
        "info": true,
        // "sDom": '<"top"<"actions">fpi<"clear">><"clear">rt<"bottom">',
        // "aaSorting": [],
        'order': [], //[[1, 'desc']]
        'processing': false,
        'serverSide': true,
        'ajax': {
            url: $('#dynamicDatatable').data('url') + $('#dynamicDatatable').data('filter'),
            dataSrc: 'data'
        },
        "rowCallback": function( row, data, index ) {
            $('.tooltip').remove();
            var updatedTime = updateTime(data.update.updated);
            if (updatedTime > 120) {
                $('td', row).addClass('obsolete');
            } else if (data.new === true && updatedTime < 4) {
                $('td', row).addClass('stylish');
                setTimeout(function() {
                    $('td', row).removeClass('stylish');
                }, 500);
            } else if (data.dynamics === 'fall' && updatedTime < 4) {
                $('td:eq(1)', row).addClass('fall');
                setTimeout(function() {
                    $('td:eq(1)', row).removeClass('fall');
                }, 500);
            } else if (data.dynamics === 'rise' && updatedTime < 4) {
                $('td:eq(1)', row).addClass('rise');
                setTimeout(function() {
                    $('td:eq(1)', row).removeClass('rise');
                }, 500);
            }},
        columns: [
            {
                data: null,
                render: function (data, type, row){
                    return '<span class="d-inline-block" tabindex="0" data-placement="top" data-toggle="tooltip" title="Нажмите для подробной информации">' +
                             '<p type="button" data-toggle="modal" data-diagram="'+row.diagram+'" data-content="'+modalWrite(row)+'" data-target="#myModal">' +
                               row.diagram +
                             '</p>' +
                           '</span>'
                },
                orderable: true
            },
            {
                data: null,
                render: function (data, type, row){
                    return '<span class="d-inline-block" tabindex="0" data-placement="top" data-toggle="tooltip" title="Нажмите для подробной информации">' +
                             '<p type="button" data-toggle="modal" data-diagram="'+row.diagram+'" data-content="'+modalWrite(row)+'" data-target="#myModal">' +
                               '<span style="color:'+colorSelector(row.marginality_percentage)+'">'+row.marginality_percentage+'% </span>' +
                               '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-info-circle" viewBox="0 0 16 16">' +
                                 '<path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>' +
                                 '<path d="m8.93 6.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM9 4.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0z"/>' +
                               '</svg>' +
                             '</p>' +
                           '</span>'
                },
                orderable: true
            },
            {
                data: null,
                render: function (data, type, row){
                    return `<p class="fw-light fs-15">< ${updateTime(row.update.updated)} cек.</p>`
                },
                orderable: false
            },
        ]
    });
    setInterval( function () {
        refreshTable.ajax.reload( null, false );
        }, 3000 );
    refreshTable.on('page.dt', function() {
        $('html, body').animate({
          scrollTop: $(".dataTables_wrapper").offset().top
        }, 'slow');
        $('thead tr th:first-child').focus().blur();
    });
});

$("#myModal").on('show.bs.modal', function (e) {
    var triggerLink = $(e.relatedTarget);
    var diagram = triggerLink.data("diagram");
    var content = triggerLink.data("content");
    $("#modalTitle").html('Инструкция к связке:<p><h5><b>'+diagram+'</h5></p>');
    $(this).find(".modal-body").html("<h5>"+content+"</h5>");
});

$( document ).ajaxComplete(function( event, request, settings ) {
    $('[data-toggle="tooltip"]').not( '[data-original-title]'
    ).tooltip();
});