from flask import Flask, request, jsonify, make_response, json
from flask_cors import cross_origin, CORS
from jsonschema import validate, ValidationError, SchemaError
from random import choice

import secrets
from exceptions import RecaptchaError, APIException
from schemas import ContactFormSchema

import requests
import logging
import jsend

app = Flask(__name__)
CORS(app)

def do_recaptcha_validation(secret, response):  
  with requests.post('https://www.google.com/recaptcha/api/siteverify', data={
    "secret": secret,
    "response": response
  }) as r:
    r.raise_for_status()
    if (r.json()['success'] != True):
      raise RecaptchaError("Non valid Recaptcha", r.error_codes)

def post_drupal_contact_message(contact, form_id):
  with requests.post(secrets.drupal_contact_message_url, json={
    "contact_form": form_id,
    "message": [contact["message"]],
    "subject": ["Contato - " + contact["name"]],
    "mail": [contact["mail"]],
    "name": [contact["name"]]
  }, auth=(secrets.drupal_auth_user, secrets.drupal_auth_password)) as r:
    r.raise_for_status()
    return r.json()

@app.route('/', methods=['POST'])
def handle_form():
  try:
    assert request.is_json  
    received_data = request.get_json()
    validate(received_data, ContactFormSchema)
    do_recaptcha_validation(secrets.recaptcha_site_key, received_data["recaptcha_response"])
    drupal_response = post_drupal_contact_message(received_data, secrets.drupal_contact_form_id)
    response = app.response_class(
      response = json.dumps(jsend.success({'data': drupal_response})),
      status = 201,
      mimetype='application/json'
    )
    return response
  except (RecaptchaError, ValidationError, AssertionError) as e:    
    raise APIException("Falha ao processar")    
  except Exception as e:
    raise APIException("Falha no servidor", 500)

@app.errorhandler(APIException)
def handle_api_exception(error):
  response = jsonify(error.to_dict())
  response.status_code = error.status_code
  logging.exception(error)
  return response