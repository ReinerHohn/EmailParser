import imaplib
import email
import csv

ifile = open("Cred.csv", "r")
reader = csv.reader(ifile)


ofile = open('Parsed.csv', 'w')
spamwriter = csv.writer(ofile, delimiter=';', quoting=csv.QUOTE_MINIMAL) #quotechar='|',

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
        retText = text.decode(charset, 'replace')
    return retText.strip()

def getEbayInBest( email_message ):
    # Body details
    body = get_decoded_email_body(email_message)
    artnr = getBodyItem(body, "Artikelnummer: ", 12)
    out=['Artikelnummer: ', artnr]
    spamwriter.writerow(out)
    stck = getBodyItem(body, "Stückzahl: ", 2)
    lieferung = getBodyItem(body, "Lieferung ca.: ", 27)
    bazahlsum = getBodyItem(body, "Bezahlt: ", 12)

def getBodyItem(body, parse_string, length):
    strRet = ""
    strName = parse_string
    pos = body.find(strName)
    length = len(strName)
    start = pos + length
    if pos > 0:
        strRet = body[start: start + 17]
    return strRet

getBestellungen()
ofile.close()
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
