import sys
sys.path.append('../src')

import app
import exceptions

import unittest

class AppTestCase(unittest.TestCase):
  def setUp(self):
    app.APP.testing = True
    self.app = app.APP.test_client()
  
  def tearDown(self):
    pass

  def test_do_recaptcha_validation_with_invalid_response(self):
    with self.assertRaises(exceptions.RecaptchaError):            
      app.do_recaptcha_validation('avocado')

  def test_do_recaptcha_validation_with_valid_recaptcha(self):            
    response = input("Digite a resposta recebida do ReCaptcha: ")    
    rv = app.do_recaptcha_validation(response)
    assert rv == True  

if __name__ == '__main__':
  unittest.main()


