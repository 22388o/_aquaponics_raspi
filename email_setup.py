def email_send_aquaponia(To: str,
                         path: str=None,
                         filename: str=None,
                         message_body:str='title\n\nbody\n\nsignature',
                         message_subject:str='subject'):
    import smtplib
    from email.mime.text import MIMEText
    if path == None:
        msg = MIMEText(message_body)
    else:
        with open(path + filename) as fp:
            msg = MIMEText(fp.read())
    # me == the sender's email address
    # you == the recipient's email address
    msg['Subject'] = message_subject
    msg['From'] = 'sziller.aquaponia@gmail.com'
    #msg['From'] = 'mepl@aukett-heese.de'
    #msg['From'] = 'szillerke@gmail.com'
    msg['To'] = To

    # Send the message via our own SMTP server.
    s = smtplib.SMTP("smtp.gmail.com", 587)
    s.ehlo ()
    s.starttls()
    s.login('sziller.aquaponia@gmail.com', 'H4lastavacska')
    s.sendmail(msg['From'], To, msg.as_string())
    s.quit()



    #s.send_message(msg)
    #s.quit()

    # Send the message via local SMTP server.



    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.

if __name__ == "__main__":
    email_send_aquaponia(To="szillerke@gmail.com", message_body="Hello Sziller!\nEz itt az automatikus uzeneted.\nOlellek:\n\nPi\n\nps.:őűíéáóüö", message_subject="tesztuzi")
