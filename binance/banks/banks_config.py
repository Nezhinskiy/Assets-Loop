from banks.banks_registration.tinkoff import IntraTinkoff, TinkoffParser
from banks.banks_registration.wise import IntraWise, WiseParser

BANKS_CONFIG = {
    'Tinkoff': {
        'bank_parser': TinkoffParser,
        'intra_exchange': IntraTinkoff,
    },
    'Wise': {
        'bank_parser': WiseParser,
        'intra_exchange': IntraWise,
    }
}
