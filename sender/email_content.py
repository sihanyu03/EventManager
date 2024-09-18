class EmailContent:
    """
    A class containing information about a single email: the email address and the personalised email contents
    """
    def __init__(self, email=None, body=None):
        self.email = email
        self.body = body
