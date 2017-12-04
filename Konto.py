import logging
from datetime import date
from fints.client import FinTS3PinTanClient

logging.basicConfig(level=logging.DEBUG)
f = FinTS3PinTanClient(
    'BLZ',  # Your bank's BLZ
    'ALIS',
    'PW',
    'ENDPOINT'  # endpoint, e.g.: https://hbci-pintan.gad.de/cgi-bin/hbciservlet
)

accounts = f.get_sepa_accounts()
print(accounts)
# [SEPAAccount(iban='DE12345678901234567890', bic='ABCDEFGH1DEF', accountnumber='123456790', subaccount='',
#              blz='123456789')]

statement = f.get_statement(accounts[0], date(2016, 12, 1), date.today())
print([t.data for t in statement])
# The statement is a list of transaction objects as parsed by the mt940 parser, see
# https://mt940.readthedocs.io/en/latest/mt940.html#mt940.models.Transaction
# for documentation. Most information is contained in a dict accessible via their
# ``data`` property

# for retrieving the holdings of an account:
holdings = f.get_holdings(accounts[0])
# holdings contains a list of namedtuple values containing ISIN, name,
# market_value, pieces, total_value and valuation_date as parsed from
# the MT535 message.