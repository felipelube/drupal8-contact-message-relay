from flask import Flask, request, jsonify, make_response, json
from jsonschema import validate, ValidationError, SchemaError
from random import choice
from secrets import recaptcha_site_key, drupal_auth_user, drupal_auth_password, drupal_contact_message_url, drupal_contact_form_id

import requests
import logging
import jsend

app = Flask(__name__)

class RecaptchaError(Exception):
  def __init__(self, message, error_codes):
    super().__init__(message)
    self.error_codes = error_codes

contact_form_schema = {
  "definitions": {}, 
  "$schema": "http://json-schema.org/draft-04/schema#", 
  "id": "http://example.com/example.json", 
  "type": "object", 
  "properties": {
    "name": {
      "id": "/properties/name", 
      "type": "string", 
      "title": "The Name Schema.", 
      "description": "An explanation about the purpose of this instance.", 
      "default": ""
    }, 
    "subject": {
      "id": "/properties/subject", 
      "type": "string", 
      "title": "The Subject Schema.", 
      "description": "An explanation about the purpose of this instance.", 
      "default": ""
    }, 
    "mail": {
      "id": "/properties/mail", 
      "type": "string", 
      "title": "The Mail Schema.", 
      "description": "An explanation about the purpose of this instance.", 
      "default": "",
      "format": "email"
    }, 
    "message": {
      "id": "/properties/message", 
      "type": "string", 
      "title": "The Message Schema.", 
      "description": "An explanation about the purpose of this instance.", 
      "default": ""
    }, 
    "recaptcha_response": {
      "id": "/properties/recaptcha_response", 
      "type": "string", 
      "title": "The Recaptcha_response Schema.", 
      "description": "An explanation about the purpose of this instance.", 
      "default": ""
    }
  }, 
  "required": [
    "name", 
    "subject", 
    "mail", 
    "message", 
    "recaptcha_response"
  ]
}

@app.route('/', methods=['POST', 'GET'])
def handle_form():
  response = ''  
  if request.method == 'POST' and request.is_json:
    received_data = request.get_json()    
    try:      
      validate(received_data, contact_form_schema)
      data_for_recaptcha = {
        "secret": recaptcha_site_key,
        "response": received_data["recaptcha_response"]
        #"remoteip":
      }
      r_recaptcha = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data_for_recaptcha)
      r_recaptcha.raise_for_status();
      jsondata = r_recaptcha.json();
      if jsondata["success"] != True:
        raise RecaptchaError("Google Recaptcha API Error", jsondata["error-codes"]) #API do Google rejeitou
      else:
        r_data_for_drupal = {
          "contact_form": drupal_contact_form_id,
          "message": [received_data["message"]],
          "subject": ["Contato"],
          "mail": [received_data["mail"]],
          "name": [received_data["name"]]
        }
        r_drupal = requests.post(drupal_contact_message_url, json=r_data_for_drupal, auth=(drupal_auth_user, drupal_auth_password))
        r_drupal.raise_for_status()
        drupal_json_data = r_drupal.json()
        response = jsonify(drupal_json_data)
    except RecaptchaError as e:
      response = app.response_class(
        response=json.dumps(jsend.fail({"recaptcha_errors": e.error_codes})),
        status=400,
        mimetype='application/json'
      )
      logging.exception(e)
    except ValidationError as e:
      response = app.response_class(
        response=json.dumps(jsend.fail({"error": "invalid data"})),
        status=400,
        mimetype='application/json'
      )
      logging.exception(e)
    except Exception as e:
      response = app.response_class(
        response=json.dumps({"error": "Server Error"}),
        status=500,
        mimetype='application/json'
      )
      logging.exception(e)

  else:        
    response = app.response_class(
      response=json.dumps({"error": "Hic sunt dracones"}),
      status=400,
      mimetype='application/json'
    )
  return response