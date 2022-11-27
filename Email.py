def email_send(to: str, path: str, filename: str):
    import smtplib
    from email.mime.text import MIMEText
    with open(path + filename) as fp:
        msg = MIMEText(fp.read())

	date = "-ma-nemreg"
    # me == the sender's email address
    # you == the recipient's email address
    msg['Subject'] = "StatusReport" + date
    #msg['From'] = 'sziller.aquaponia@gmail.com'
    #msg['From'] = 'mepl@aukett-heese.de'
    msg['From'] = 'szillerke@gmail.com'
    msg['To'] = to

    # Send the message via our own SMTP server.
    s = smtplib.SMTP("smtp.gmail.com", 587)
    #s = smtplib.SMTP("remote.aukett-heese.de", 443)
    s.ehlo ()
    s.starttls()
    s.login('sziller.aquaponia@gmail.com', 'H4lastavacska')
    #s.login('mepl', '13*AH#mepl')
    s.sendmail(msg['From'], to, msg.as_string())
    # s.sendmail('mepl@aukett-heese.de', to, msg.as_string())
    s.quit()



    #s.send_message(msg)
    #s.quit()

    # Send the message via local SMTP server.



    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.

if __name__ == "__main__":
    email_send(to="szillerke@gmail.com", path="", filename="")
