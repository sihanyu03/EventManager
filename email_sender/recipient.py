class Recipient:
    def __init__(self, email=None, text=None):
        if email is not None:
            self.email = email
        if text is not None:
            self.text = text
