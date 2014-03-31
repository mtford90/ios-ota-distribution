import mandrill

__author__ = 'mtford'


class BaseEmail(object):

    MandrillAPIKey = '65cf183c-655e-4f81-ae7e-00f5f2f7e5f2'

    def __init__(self, from_email, to_emails, message, from_name=None, subject=None):
        super(BaseEmail, self).__init__()
        self.message = message
        self.mandrill = mandrill.Mandrill(BaseEmail.MandrillAPIKey)
        self.result = None
        self.from_email = from_email
        self.to_emails = to_emails
        self.from_name = from_name
        self.subject = subject
        self.success = False
        self.sent = False

    def send(self):
        email = {
            'html': self.message,
            'from_email': self.from_email,
            'to': [{'email': x} for x in self.to_emails]
        }
        if self.from_name:
            email['from_name'] = self.from_name
        if self.subject:
            email['subject'] = self.subject
        self.result = self.mandrill.messages.send(email)
        self.sent = True
        self.success = self.result[0]['status'] == 'sent'


