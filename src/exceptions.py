'''
Exceptions used in the API
'''
import jsend

class RecaptchaError(Exception):
    ''' A Recaptcha Exception '''
    def __init__(self, message, error_codes):
        super().__init__(self)
        self.message = message
        self.error_codes = error_codes
    
    def __str__(self):
        return "{} .\nReturned error codes: {}".format(
            self.message, self.error_codes)

class APIException(Exception):
    ''' A Generic API Exception '''
    status_code = 400
    def __init__(self, message, status_code=None, payload=None):
        ''' Constructor '''
        super().__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        ''' Transforms this exception to a dict '''
        if self.status_code >= 400 and self.status_code < 500:
            result = dict(jsend.fail({
                'message': self.message,
                'payload': self.payload
            }))
        elif self.status_code >= 500:
            result = dict(jsend.error(self.message, self.status_code, self.payload))
        return result
