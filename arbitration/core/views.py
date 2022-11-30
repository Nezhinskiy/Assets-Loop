import time

from django.shortcuts import redirect
from django.views.generic import ListView

from core.models import InfoLoop
from core.multithreading import all_exchanges
from core.registration import all_registration
from celery import group, chord, chain
from banks.tasks import parse_internal_tinkoff_rates, parse_internal_wise_rates, parse_currency_market_tinkoff_rates, best_bank_intra_exchanges
from crypto_exchanges.tasks import crypto_exchanges_start_time, get_tinkoff_p2p_binance_exchanges, get_wise_p2p_binance_exchanges, get_all_binance_crypto_exchanges, get_binance_card_2_crypto_exchanges, get_all_card_2_wallet_2_crypto_exchanges, best_crypto_exchanges_intra_exchanges


from core.tasks import end_all_exchanges, end_crypto_exchanges, end_banks_exchanges, get_simpl_binance_tinkoff_inter_exchanges_calculate, get_simpl_binance_wise_inter_exchanges_calculate, get_complex_binance_tinkoff_inter_exchanges_calculate, get_complex_binance_wise_inter_exchanges_calculate


class InfoLoopList(ListView):
    model = InfoLoop
    template_name = 'core/home.html'

    def get_queryset(self):
        return self.model.objects.all()

    def get_context_data(self, **kwargs):
        context = super(InfoLoopList, self).get_context_data(**kwargs)
        context['info_loops'] = self.get_queryset()
        context['last_update'] = self.get_queryset().latest(
            'updated').updated
        context['loops_count'] = self.get_queryset().filter(value=1).count
        return context


def get_all_exchanges(request):
    return all_exchanges()


# def start(request):
#     InfoLoop.objects.create(value=True)
#
#     group_crypto_exchanges = group(
#         crypto_exchanges_start_time.s(), get_tinkoff_p2p_binance_exchanges.s(),
#         get_wise_p2p_binance_exchanges.s(),
#         chord(
#             get_all_binance_crypto_exchanges.s(),
#             get_all_card_2_wallet_2_crypto_exchanges.s()
#         ),
#         get_binance_card_2_crypto_exchanges.s(),
#     )
#     crypto_exchanges = chord(group_crypto_exchanges,
#                              best_crypto_exchanges_intra_exchanges.s())
#
#     group_banks = group(
#         bank_start_time.s(), parse_internal_tinkoff_rates.s(),
#         parse_internal_wise_rates.s(), parse_currency_market_tinkoff_rates.s()
#     )
#     banks = chord(group_banks, best_bank_intra_exchanges.s())
#
#     general_group = group(crypto_exchanges, banks)
#
#     end_group = group(
#         get_simpl_binance_tinkoff_inter_exchanges_calculate.s(),
#         get_simpl_binance_wise_inter_exchanges_calculate.s(),
#         get_complex_binance_tinkoff_inter_exchanges_calculate.s(),
#         get_complex_binance_wise_inter_exchanges_calculate.s()
#     )
#     all = chord(general_group, end_group)
#     main = chord(
#         group(all_start_time.s(), all), best_get_inter_exchanges_calculate.s()
#     )
#     main.delay()
#     return redirect('core:home')


def start(request):
    redirect('crypto_exchanges:InterExchangesListNew')
    # 1. Crypto exchanges
    # 1.1 Binance
    # 1.1.1 Tinkoff
    group_tinkoff_inter_exchanges_calculate = group(
        get_complex_binance_tinkoff_inter_exchanges_calculate.s(),
        get_simpl_binance_tinkoff_inter_exchanges_calculate.s()
    )
    group_tinkoff_binance_p2p = group(get_tinkoff_p2p_binance_exchanges.s())
    chord_tinkoff_binance_p2p = chord(
        group_tinkoff_binance_p2p,
        get_simpl_binance_tinkoff_inter_exchanges_calculate.s()
    )
    # 1.1.2 Wise
    group_wise_inter_exchanges_calculate = group(
        get_complex_binance_wise_inter_exchanges_calculate.s(),
        get_simpl_binance_wise_inter_exchanges_calculate.s()
    )
    group_wise_binance_p2p = group(get_wise_p2p_binance_exchanges.s())
    chord_wise_binance_p2p = chord(
        group_wise_binance_p2p,
        get_simpl_binance_wise_inter_exchanges_calculate.s()
    )
    # 1.0 All banks
    group_all_bank_complex_inter_exchanges_calculate = group(
        get_complex_binance_tinkoff_inter_exchanges_calculate.s(),
        get_complex_binance_wise_inter_exchanges_calculate.s(),
    )
    group_all_banks_inter_exchanges_calculate = group(
        group_tinkoff_inter_exchanges_calculate,
        group_wise_inter_exchanges_calculate
    )
    group_all_banks_binance_crypto_exchanges = group(
        chord(
            get_all_binance_crypto_exchanges.s(),
            get_all_card_2_wallet_2_crypto_exchanges.s()
        ), get_binance_card_2_crypto_exchanges.s()
    )
    chord_binance_crypto_exchanges = chord(
        group_all_banks_binance_crypto_exchanges,
        group_all_banks_inter_exchanges_calculate
    )

    # 2. Banks
    # 2.1 Tinkoff
    group_tinkoff_rates = group(parse_internal_tinkoff_rates.s(),
                                parse_currency_market_tinkoff_rates.s())
    chord_tinkoff_rates = chord(
        group_tinkoff_rates,
        get_simpl_binance_tinkoff_inter_exchanges_calculate.s()
    )
    # 2.2 Wise
    group_wise_rates = group(parse_internal_tinkoff_rates.s())
    chord_wise_rates = chord(
        group_wise_rates, get_simpl_binance_wise_inter_exchanges_calculate.s()
    )

    # General
    # 0.1 Crypto exchanges
    general_group_crypto_exchanges = group(
        chord_tinkoff_binance_p2p, chord_wise_binance_p2p,
        chord_binance_crypto_exchanges
    )
    general_chord_crypto_exchanges = chord(chord(
        general_group_crypto_exchanges,
        group_all_bank_complex_inter_exchanges_calculate
    ), end_crypto_exchanges.s())
    # 0.2 Banks
    general_group_banks_exchanges = group(
        chord_tinkoff_rates, chord_wise_rates
    )
    general_chord_banks_exchanges = chord(chord(
        general_group_banks_exchanges,
        group_all_bank_complex_inter_exchanges_calculate
    ), end_banks_exchanges.s())
    # 0.
    general_group = group(
        general_chord_crypto_exchanges, general_chord_banks_exchanges
    )
    general_chord = chord(general_group,
                          end_all_exchanges.s())
    if InfoLoop.objects.last().value == 0:
        InfoLoop.objects.create(value=True)
        count_loop = 0
        while InfoLoop.objects.last().value == 1:
            general_chord.delay()
            while (InfoLoop.objects.last().value == 1
                    and not InfoLoop.objects.last().all_exchanges):
                time.sleep(1)
            if (
                    InfoLoop.objects.last().all_crypto_exchanges
                    and InfoLoop.objects.last().all_banks_exchanges
            ):
                count_loop += 1
                if count_loop > 10:
                    InfoLoop.objects.create(value=False)
                else:
                    InfoLoop.objects.create(value=True)
            else:
                InfoLoop.objects.create(value=False)
    return redirect('crypto_exchanges:InterExchangesListNew')


def stop(request):
    if InfoLoop.objects.last().value == 1:
        InfoLoop.objects.create(value=False)
    return redirect('core:info')


def registration(request):
    all_registration()
    return redirect('core:info')
