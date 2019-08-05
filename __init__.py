import fineco
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json


def send_email(content, smtp):
    s = smtplib.SMTP(host=smtp.get('host'), port=smtp.get('port'))
    s.starttls()
    s.login(smtp.get('email'), smtp.get('password'))

    msg = MIMEMultipart()

    msg['From'] = smtp.get('email')
    msg['To'] = smtp.get('recipient')
    msg['Subject'] = "Fineco Results"

    msg.attach(MIMEText(content, 'plain'))

    s.send_message(msg)
    s.quit()


if __name__ == "__main__":

    try:
        with open('conf.json') as json_file:
            conf = json.load(json_file)
    except:
        print("Something went wrong opening configuration")
        exit(0)

    _scan_fineco = False
    smtp = conf['smtp']

    if len(sys.argv) > 1:
        if sys.argv[1] == "1":
            _scan_fineco = True

    print("Scan before is set on %d" % _scan_fineco)

    fin = fineco.Fineco.login(conf['username'], conf['password'])
    if fin is not None:
        print("Hello, %s" % fin.get_name())

        if not fin.exists_quotation_file():
            print("Quotation file doesn't exists, we'll recreate file.")
            _scan_fineco = True

        if _scan_fineco:
            fin.scan(save_in_file=True)

        fin.collect_data()

        result = fin.capture_result(conf.get('valid_results'))

        send_email(result, smtp)

    else:
        print("Login is wrong")
