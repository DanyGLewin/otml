import logging
import smtplib

from src.models.singelton import Singleton

logger = logging.getLogger(__name__)


class MailManager(Singleton):

    def __init__(self):
        self.sender = "otml.results@gmail.com"
        self.recipient = "iddoberger@gmail.com"

        self.user_name = "otml.results@gmail.com"
        self.password = "otmlotml"
        self.subject = "simulation notification"

    def send_mail(self, log_segment, log_file_name):

        body = log_segment
        body = body + "<br>" + log_file_name
        body = "" + body + ""

        headers = [
            "From: " + self.sender,
            "Subject: " + self.subject + " " + log_file_name,
            "To: " + self.recipient,
            "MIME-Version: 1.0",
            "Content-Type: text/html",
        ]
        headers = "\r\n".join(headers)

        msg = headers + "\r\n\r\n" + body

        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)  # or port 465 doesn't seem to work!
            server.ehlo()
            server.starttls()
            server.login(self.user_name, self.password)
            sendmail_result = server.sendmail(self.sender, self.recipient, msg)
            server.close()
            logger.debug(sendmail_result)
            logger.info("Email successfully sent")
        except:
            logger.info("Failed to send mail")
