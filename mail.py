import mandrill

__author__ = 'mtford'


class BaseEmail(object):

    def __init__(self, api_key):
        super(BaseEmail, self).__init__()
        self.mandrill = mandrill.Mandrill(api_key)
        self.result = None
        self.success = False
        self.sent = False

    def send(self, from_email, to_emails, html, from_name=None, subject=None):
        email = {
            'html': html,
            'from_email': from_email,
            'to': [{'email': x} for x in to_emails],
            'from_name': from_name,
            'subject': subject
        }
        self.result = self.mandrill.messages.send(email)
        self.sent = True
        self.success = self.result[0]['status'] == 'sent'


