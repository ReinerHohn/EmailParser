import imaplib
import email
import csv

ifile = open("Cred.csv", "r")
reader = csv.reader(ifile)

for row in reader:
    username = row[0]
    pwd = row[1]

mail = imaplib.IMAP4_SSL("imap.gmx.net")
mail.login(username, pwd)
result, mailboxlist = mail.list()
#for i in mailboxlist:
#    print(i)

mail.select('"INBOX/GELD/Best - Bezahlung"') #mailboxlist[0])
result, data = mail.uid('search', None, '(FROM "service@paypal.de")' )
#result, data = mail.uid('search', None, '(FROM "Autodesk" SUBJECT "Reset")' )
#result, data = mail.uid('search', None, "UNSEEN") # (ALL/UNSEEN)
i = len(data[0].split())

for x in range(i):
    latest_email_uid = data[0].split()[x]
    result, email_data = mail.uid('fetch', latest_email_uid, '(RFC822)')
    # result, email_data = conn.store(num,'-FLAGS','\\Seen')
    # this might work to set flag to seen, if it doesn't already
    raw_email = email_data[0][1]
    raw_email_string = raw_email.decode('utf-8')
    email_message = email.message_from_string(raw_email_string)

    # Header Details
    #date_tuple = email.utils.parsedate_tz(email_message['Date'])
    #if date_tuple:
    #    local_date = datetime.datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
    #    local_message_date = "%s" %(str(local_date.strftime("%a, %d %b %Y %H:%M:%S")))
    #email_from = str(email.header.make_header(email.header.decode_header(email_message['From'])))
    #email_to = str(email.header.make_header(email.header.decode_header(email_message['To'])))
    #subject = str(email.header.make_header(email.header.decode_header(email_message['Subject'])))

    # Body details
    for part in email_message.walk():
        if part.get_content_type() == "text/plain":
            body = part.get_payload(decode=True)
            strName="Transaktionscode: ".encode('utf-8')
            pos = body.find(strName)
            length =  len(strName)
            start = pos + length
            if pos > 0:
                transactioncode = body[start: start + 17]

            print(transactioncode)
            strName = "Artikelnr.".encode('utf-8')
            pos = body.find(strName)
            length = len(strName)
            start = pos + length
            if pos > 0:
                artnr = body[start: start + 12]
                print(artnr)
            # Rechnungsnummer:
            #file_name = "email_" + str(x) + ".txt"
            #output_file = open(file_name, 'w')
            #output_file.write("From: %s\nTo: %s\nDate: %s\nSubject: %s\n\nBody: \n\n%s" %(email_from, email_to,local_message_date, subject, body.decode('utf-8')))
            #output_file.close()
        else:
            continue