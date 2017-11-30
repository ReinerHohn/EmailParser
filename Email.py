import imaplib
import email
import csv
import datetime
import re

ifile = open("Cred.csv", "r")
reader = csv.reader(ifile)

id_dict = { "0": "0"}

iofileEbay = open('EbayParsed2.csv', 'w+', newline='')
ebaywriter = csv.writer(iofileEbay, delimiter=';', quoting=csv.QUOTE_MINIMAL) #quotechar='|',
ebayreader = csv.reader(iofileEbay)

out = ["Artikelnummer: ", "Stückzahl: ", "Lieferung ca.: ", "Bezahlt: "]
ebaywriter.writerow(out)

iofilePP = open('PaypalParsed3.csv', 'w+', newline='')
paypalwriter = csv.writer(iofilePP, delimiter=';', quoting=csv.QUOTE_MINIMAL)
out = ["Artikelnummer: ", "Transactionsnummer: ", "Betreff", "Datum" ]
paypalwriter.writerow(out)

for row in reader:
    username = row[0]
    pwd = row[1]

mail = imaplib.IMAP4_SSL("imap.gmx.net")
mail.login(username, pwd)
result, mailboxlist = mail.list()
#for i in mailboxlist:
#    print(i)

def getEmailsInAndFrom(inbox, fromEmail, pfktptr):
    mail.select(inbox)
    result, data = mail.uid('search', None, "ALL") # UNSEEN
    i = len(data[0].split())
    for x in range(i):
        latest_email_uid = data[0].split()[x]
        result, email_data = mail.uid('fetch', latest_email_uid, '(RFC822)')
        raw_email = email_data[0][1]
        try:
            raw_email_string = raw_email.decode('utf-8')
        except:
            print("mail" + str(x) + "ging nit")
        email_message = email.message_from_string(raw_email_string)

        date_tuple = email.utils.parsedate_tz(email_message['Date'])
        if date_tuple:
            jaja = email.utils.mktime_tz(date_tuple)
            local_date = datetime.datetime.fromtimestamp(jaja)
            local_message_date = "%s" % (str(local_date.strftime("%a, %d %b %Y %H:%M:%S")))

        subject = str(email.header.make_header(email.header.decode_header(email_message['Subject'])))

        email_from = str(email.header.make_header(email.header.decode_header(email_message['From'])))
        print( fromEmail + " " + email_from)
        if fromEmail in email_from:
            pfktptr(email_message, subject, local_message_date)

def getBestellungen():
    getEmailsInAndFrom('"INBOX/GELD/Best"', "ebay@ebay.de", getEbayInBest)

def getBezahlungen():
    getEmailsInAndFrom('"INBOX/GELD/Best - Bezahlung"', "service@paypal.de", getPaypalInBez)

def get_decoded_email_body(msg):
    """ Decode email body.
    Detect character set if the header is not set.
    We try to get text/plain, but if there is not one then fallback to text/html.
    :param message_body: Raw 7-bit message body input e.g. from imaplib. Double encoded in quoted-printable and latin-1
    :return: Message body as unicode string
    """

    text = ""
    if msg.is_multipart():
        html = None
        for part in msg.walk():
        # r part in msg.get_payload():
            print ("%s, %s" % (part.get_content_type(), part.get_content_charset()))

            if part.get_content_charset() is None:
                # We cannot know the character set, so return decoded "something"
                text = part.get_payload(decode=True)
                continue

            charset = part.get_content_charset()

            if part.get_content_type() == 'text/plain':
                text = part.get_payload(decode=True)
                retText = text.decode(charset, 'replace')

            if part.get_content_type() == 'text/html':
                html = part.get_payload(decode=True)
                retText = html.decode(charset, 'replace')

        return retText.strip()
    else:
        text = msg.get_payload(decode=True)
        charset = msg.get_content_charset()
        retText = text.decode(charset, 'replace')
        #if part.get_content_type() == 'text/plain':
        #if msg.get_content_type() == 'text/html':

    return retText.strip()

def getEbayInBest( email_message, subject, date_local ):
    # Body details
    body = get_decoded_email_body(email_message)
    artnr = getBodyItem(body, "Artikelnummer: ", 12)
    if artnr == "":
        artnr = getBodyItem(body, "Artikelnr.: ", 12)
    stck = getBodyItem(body, "Stückzahl: ", 2)
    lieferung = getBodyItem(body, "Lieferung ca.: ", 27)
    bezahlsum = getBodyItem(body, "Bezahlt: ", 12)
    getBodyItemDelimited(body, "Bezahlt: EUR ", " mit")
    out = [artnr, subject, date_local, stck, lieferung, bezahlsum]
    id_dict[artnr]={"artnr" : artnr, "subject" : subject, "date_local" : date_local, "stck" : stck, "lieferung":lieferung, "bezahlsum":bezahlsum }
    try:
        ebaywriter.writerow(out)
    except:
        print("ging nit ebay write")
def getPaypalInBez( email_message, subject, date_local ):
    # Body details
    body = get_decoded_email_body(email_message)
    artnr = getBodyItemDelimited(body, "Artikelnummer: ", "<")
    if artnr == "":
        artnr = getBodyItemDelimited(body, "Artikelnr.: ", "<")
    if artnr == "":
        artnr = getBodyItemDelimited(body, "Artikelnr. ", "<")
    if artnr == "":
        artnr = getBodyItemDelimited(body, "Artikelnr.", "<")

    transact = getBodyItem(body, 'Transaktionscode: <a target="new" href="https://www.paypal.com/de/cgi-bin/webscr?cmd=_view-a-trans&amp;id=', 17)
    if transact == "":
        id = transact = getBodyItem(body, "Transaktionscode: ", 17)
    if artnr == "":
        i = 2
    if transact == "":
        id = transact = getBodyItem(body, "id=", 17)


    if artnr in id_dict:
        ret = id_dict[artnr]
        out = [artnr, transact, subject, date_local, ret["artnr"], ret["stck"], ret["subject"], ret["date_local"], ret["lieferung"], ret["bezahlsum"]]
    else:
        out = [artnr, transact, subject, date_local]
    try:
        paypalwriter.writerow(out)
    except:
        print("Paypal write ging nit")

def getBodyItemDelimited(body, parse_string, endstr):
    strRet = ""
    lenght = len(body)
    startpos = body.find(parse_string)
    if startpos > 0:
        endpos = body.find(endstr, startpos)
        length = endpos - startpos
        return getBodyItem(body, parse_string, length)
    else:
        return ""
def getBodyItem(body, parse_string, length_item):
    strRet = ""
    find_pos = body.find(parse_string)
    length_parse_str = len(parse_string)
    if find_pos > 0:
        # Finde start des Suchstrings hinter suchtoken
        start = find_pos + length_parse_str
        strFound = body[start: start + length_item]
        strRet = strFound

        # suche illegale Zeichen
        start_inval = re.search('<|\\|>|\\n', strFound)
        while start_inval != None:
            first_ill = start_inval.end()
            # Schneide vorne die illegalen Zeichen ab
            strRet = strRet[:first_ill - 1]
            start_inval = re.search('<|\\|>|\\n', strRet)

        # Erstes gültiges Zeichen holen
        start_alpha_num = re.search('[A-Z]|[0-9]|[a-z]', strRet)
        if None != start_alpha_num:
            start_num_pos = start_alpha_num.start()
            # Schneide vorne die nicht alpha-num Zeichen ab
            strRet = strRet[start_num_pos:]
            end_alpha_num = re.search('<|\\|>|\\n', strRet)
            if None != end_alpha_num:
                strRet = strRet[end_alpha_num.end() ]
    return strRet

def getBodyItemFromStartIndex(body, index, parse_string, length):
    strRet = ""
    strName = parse_string
    pos = body.find(strName, index)
    length = len(strName)
    start = pos + length
    if pos > 0:
        strRet = body[start: start + 17]
    return strRet, pos

getBestellungen()
getBezahlungen()
iofileEbay.close()
iofilePP.close()
ifile.close()
