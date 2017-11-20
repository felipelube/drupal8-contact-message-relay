'''
An small API for relaying contact messages to Drupal after server-side Recaptcha validation.
'''
import logging
from exceptions import RecaptchaError, APIException
import jsend
import requests


from flask import Flask, jsonify, json, request
from flask_cors import CORS
from jsonschema import ValidationError, validate
from schemas import CONTACT_FORM_SCHEMA

APP = Flask(__name__)
APP.config.from_object('config')

def do_recaptcha_validation(response):
    ''' Perform a server-side Google ReCaptcha validation '''    
    with requests.post('https://www.google.com/recaptcha/api/siteverify', data={
        "secret": APP.config["RECAPTCHA_SECRET_KEY"],
        "response": response
    }) as req:
        req.raise_for_status()
        json_response = req.json()
        try:            
            assert json_response['success'] == True
        except AssertionError:
            raise RecaptchaError("Invalid", json_response['error-codes'])        
        else:
            return True

def post_drupal_contact_message(contact):
    ''' Post contact message to Drupal '''
    with requests.post(app.config["DRUPAL_CONTACT_MESSAGE_URL"], json={
        "contact_form": APP.config["DRUPAL_CONTACT_FORM_ID"],
        "message": [contact["message"]],
        "subject": ["Contato - " + contact["name"]],
        "mail": [contact["mail"]],
        "name": [contact["name"]]
    }, auth=(app.config["DRUPAL_AUTH_USER"], app.config["DRUPAL_AUTH_PASSWORD"])) as req:
        req.raise_for_status()
        return req.json()

@APP.route('/', methods=['POST'])
def handle_form():    
    ''' Web entrypoint '''
    try:
        assert request.is_json        
        received_data = request.get_json()
        validate(received_data, CONTACT_FORM_SCHEMA)
        do_recaptcha_validation(received_data["recaptcha_response"])
        drupal_response = post_drupal_contact_message(received_data)
        response = APP.response_class(
            response=json.dumps(jsend.success({'data': drupal_response})),
            status=201,
            mimetype='application/json'
        )
        return response
    except (RecaptchaError, ValidationError, AssertionError):
        raise APIException("Invalid captcha or bad request")
    except Exception:
        raise APIException("Server error", 500)

@APP.errorhandler(APIException)
def handle_api_exception(error):
    '''Global error handler'''
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    logging.exception(error)
    return response
