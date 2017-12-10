import re

import logging
from datetime import date
from fints.client import FinTS3PinTanClient

import Datenbank

def getBelegField(field_id, strFileBeleg ):
    strFieldId = ""
    posFiledId = re.search(field_id, strFileBeleg)
    if None != posFiledId:
        strFieldId=strFileBeleg[posFiledId.end():]
        start_space = re.search(' ', strFieldId)
        if None != start_space:
            start_space_pos = start_space.end()
            strFieldId = strFieldId[start_space_pos:]
            end_alpha_num = re.search('[^0-9]', strFieldId)
            if None != end_alpha_num:
                strFieldId=strFieldId[:end_alpha_num.start()]
    return strFieldId

ifile = open("Beleg.txt", "r")
strFileBeleg=ifile.read()
terminal_id = getBelegField("Terminal", strFileBeleg)
ta_nr = getBelegField("TA", strFileBeleg)
ta_nr = getBelegField("Ta", strFileBeleg)
genem_nr = getBelegField("Genehm", strFileBeleg)


def getBankTransactions(pw_dict):
    logging.basicConfig(level=logging.DEBUG)
    f = FinTS3PinTanClient(
       pw_dict['VB_BLZ'],  # Your bank's BLZ
       pw_dict['VB_ALIAS'],
       pw_dict['VB_PW'],
       pw_dict['VB_ENDP']  # endpoint, e.g.: https://hbci-pintan.gad.de/cgi-bin/hbciservlet
    )

    accounts = f.get_sepa_accounts()
    print(accounts)

    statement = f.get_statement(accounts[0], date(2017, 10, 21), date.today())
    for t in statement:
        amount = t.data['amount'].amount
        vb_date=t.data['date']
        try:
            transaction_details = t.data['transaction_details']
        except:
            print( "Hat kein transaction_details")
        parseIban(amount, vb_date, transaction_details)
    # The statement is a list of transaction objects as parsed by the mt940 parser, see
    # https://mt940.readthedocs.io/en/latest/mt940.html#mt940.models.Transaction
    # for documentation. Most information is contained in a dict accessible via their
    # ``data`` property

    # for retrieving the holdings of an account:
    holdings = f.get_holdings(accounts[0])
    # holdings contains a list of namedtuple values containing ISIN, name,
    # market_value, pieces, total_value and valuation_date as parsed from
    # the MT535 message.

def parseIban(amount, vb_date, transaction_details):
    eref = getIbanField(transaction_details, "EREF+")
    mref = getIbanField(transaction_details, "MREF+")
    cred = getIbanField(transaction_details, "CRED+")
    svwz = getIbanField(transaction_details, "SVWZ+")
    if eref != "":
        saveIban(amount, vb_date, eref, mref, cred, svwz)

def saveIban(betrag, datum, eref, mref, cred, svwz):
    terminal_id = eref[:8]
    ta_nr = eref[8:14]
    #datum= eref[14:20]
    end_genem = re.search('\?', mref)
    if None != end_genem:
        genemigungs_nr= mref[:end_genem.end() - 1 ]
    verwend_zw = svwz.replace(",", " ")


    belegDb.insertBeleg(terminal_id, ta_nr, genemigungs_nr, verwend_zw, betrag, datum)

def getIbanField(text, field_id):
    field = ""
    start_field_id = re.search(field_id, text)
    if start_field_id != None:
        field_first = start_field_id.end()
        field = text[field_first + 1:]
        end_field = re.search(' ', field)
        if end_field != None:
            field = field[:end_field.start() ]
    return field
getBankTransactions(pw_dict)

