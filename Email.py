import imaplib
import email
import csv

ifile = open("Cred.csv", "r")
reader = csv.reader(ifile)


ofile = open('EbayParsed.csv', 'w')
ebaywriter = csv.writer(ofile, delimiter=';', quoting=csv.QUOTE_MINIMAL) #quotechar='|',
ofilePP = open('PaypalParsed2.csv', 'w')
paypalwriter = csv.writer(ofilePP, delimiter=';', quoting=csv.QUOTE_MINIMAL)

for row in reader:
    username = row[0]
    pwd = row[1]

mail = imaplib.IMAP4_SSL("imap.gmx.net")
mail.login(username, pwd)
result, mailboxlist = mail.list()
#for i in mailboxlist:
#    print(i)

def getBestellungen():
    mail.select('"INBOX/GELD/Best"')
    result, data = mail.uid('search', None, "UNSEEN")
    i = len(data[0].split())
    for x in range(i):
        latest_email_uid = data[0].split()[x]
        result, email_data = mail.uid('fetch', latest_email_uid, '(RFC822)')
        raw_email = email_data[0][1]
        raw_email_string = raw_email.decode('utf-8')
        email_message = email.message_from_string(raw_email_string)

        email_from = str(email.header.make_header(email.header.decode_header(email_message['From'])))
        if "ebay@ebay.de" in email_from:
            getEbayInBest( email_message )
        # subject = str(email.header.make_header(email.header.decode_header(email_message['Subject'])))

def getBezahlungen():
    mail.select('"INBOX/GELD/Best - Bezahlung"')
    result, data = mail.uid('search', None, "UNSEEN")
    i = len(data[0].split())
    for x in range(i):
        try:
            latest_email_uid = data[0].split()[x]
            result, email_data = mail.uid('fetch', latest_email_uid, '(RFC822)')
            raw_email = email_data[0][1]
            raw_email_string = raw_email.decode('utf-8')
            email_message = email.message_from_string(raw_email_string)

            email_from = str(email.header.make_header(email.header.decode_header(email_message['From'])))
            if "service@paypal.de" in email_from:
                getPaypalInBez( email_message )
            # subject = str(email.header.make_header(email.header.decode_header(email_message['Subject'])))
        except UnicodeDecodeError:
            print( "nummer ist" + str(i))


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

def getEbayInBest( email_message ):
    # Body details
    body = get_decoded_email_body(email_message)
    artnr = getBodyItem(body, "Artikelnummer: ", 12)
    if artnr == "":
        artnr = getBodyItem(body, "Artikelnr.: ", 12)
    stck = getBodyItem(body, "Stückzahl: ", 2)
    lieferung = getBodyItem(body, "Lieferung ca.: ", 27)
    bazahlsum = getBodyItem(body, "Bezahlt: ", 12)
    out = ['Artikelnummer: ', artnr, "Stückzahl: ", stck, "Lieferung ca.: ", lieferung, "Bezahlt: ", bazahlsum]
    ebaywriter.writerow(out)

def getPaypalInBez( email_message ):
    # Body details
    body = get_decoded_email_body(email_message)
    artnr = getBodyItem(body, "Artikelnummer: ", 12)
    if artnr == "":
        artnr = getBodyItem(body, "Artikelnr.: ", 12)
    if artnr == "":
        artnr = getBodyItem(body, "Artikelnr. ", 12)

    transact = getBodyItemFromStartIndex(body, body.find("Transaktionscode: < a: "), "id=", 17)
    if transact == "":
        id = transact = getBodyItem(body, "Transaktionscode: ", 17)
    if artnr == "":
        i = 2
    if transact == "":
        id = transact = getBodyItem(body, "id=", 17)
    out = ['Artikelnummer: ', artnr, "Transactionsnummer: ", transact]
    paypalwriter.writerow(out)

def getBodyItem(body, parse_string, length):
    strRet = ""
    strName = parse_string
    pos = body.find(strName)
    length = len(strName)
    start = pos + length
    if pos > 0:
        strRet = body[start: start + 17]
    return strRet, pos

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
ofile.close()
ofilePP.close()
ifile.close()


#mail.select('"INBOX/GELD/Best - Bezahlung"') #mailboxlist[0])
#result, data = mail.uid('search', None, '(FROM "service@paypal.de")' )
#result, data = mail.uid('search', None, '(FROM "Autodesk" SUBJECT "Reset")' )
#result, data = mail.uid('search', None, "UNSEEN") # (ALL/UNSEEN)
#i = len(data[0].split())


 # Header Details
    #date_tuple = email.utils.parsedate_tz(email_message['Date'])
    #if date_tuple:
    #    local_date = datetime.datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
    #    local_message_date = "%s" %(str(local_date.strftime("%a, %d %b %Y %H:%M:%S")))
    #email_from = str(email.header.make_header(email.header.decode_header(email_message['From'])))
    #email_to = str(email.header.make_header(email.header.decode_header(email_message['To'])))
    #subject = str(email.header.make_header(email.header.decode_header(email_message['Subject'])))

 #file_name = "email_" + str(x) + ".txt"
            #output_file = open(file_name, 'w')
            #output_file.write("From: %s\nTo: %s\nDate: %s\nSubject: %s\n\nBody: \n\n%s" %(email_from, email_to,local_message_date, subject, body.decode('utf-8')))
            #output_file.close()
#"Transaktionscode: "Artikelnr."
