from django.shortcuts import redirect
from django.views.generic import ListView

from core.models import InfoLoop
from core.multithreading import all_exchanges
from core.registration import all_registration
from celery import group, chord, chain
from banks.tasks import bank_start_time, parse_internal_tinkoff_rates, parse_internal_wise_rates, parse_currency_market_tinkoff_rates, best_bank_intra_exchanges
from crypto_exchanges.tasks import crypto_exchanges_start_time, get_tinkoff_p2p_binance_exchanges, get_wise_p2p_binance_exchanges, get_all_binance_crypto_exchanges, get_binance_card_2_crypto_exchanges, get_all_card_2_wallet_2_crypto_exchanges, best_crypto_exchanges_intra_exchanges


from core.tasks import all_start_time, best_get_inter_exchanges_calculate, all_end, get_simpl_binance_tinkoff_inter_exchanges_calculate, get_simpl_binance_wise_inter_exchanges_calculate, get_complex_binance_tinkoff_inter_exchanges_calculate, get_complex_binance_wise_inter_exchanges_calculate


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


def start(request):
    InfoLoop.objects.create(value=True)

    group_crypto_exchanges = group(
        crypto_exchanges_start_time.s(), get_tinkoff_p2p_binance_exchanges.s(),
        get_wise_p2p_binance_exchanges.s(),
        chord(
            get_all_binance_crypto_exchanges.s(),
            get_all_card_2_wallet_2_crypto_exchanges.s()
        ),
        get_binance_card_2_crypto_exchanges.s(),
    )
    crypto_exchanges = chord(group_crypto_exchanges,
                             best_crypto_exchanges_intra_exchanges.s())

    group_banks = group(
        bank_start_time.s(), parse_internal_tinkoff_rates.s(),
        parse_internal_wise_rates.s(), parse_currency_market_tinkoff_rates.s()
    )
    banks = chord(group_banks, best_bank_intra_exchanges.s())

    general_group = group(crypto_exchanges, banks)

    end_group = group(
        get_simpl_binance_tinkoff_inter_exchanges_calculate.s(),
        get_simpl_binance_wise_inter_exchanges_calculate.s(),
        get_complex_binance_tinkoff_inter_exchanges_calculate.s(),
        get_complex_binance_wise_inter_exchanges_calculate.s()
    )
    all = chord(general_group, end_group)
    main = chord(group(all_start_time.s(), all), best_get_inter_exchanges_calculate.s())
    main.delay()
    return redirect('core:home')


def stop(request):
    if InfoLoop.objects.last().value == 1:
        InfoLoop.objects.create(value=False)
    return redirect('core:home')


def registration(request):
    all_registration()
    return redirect('core:home')