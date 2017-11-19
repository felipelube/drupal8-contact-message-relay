'''
An small API for relaying contact messages to Drupal after server-side Recaptcha validation.
'''
import logging
import secrets
from exceptions import RecaptchaError, APIException
import jsend
import requests


from flask import Flask, jsonify, json, request
from flask_cors import CORS
from jsonschema import ValidationError, validate
from schemas import CONTACT_FORM_SCHEMA

APP = Flask(__name__)
CORS(APP)

def do_recaptcha_validation(secret, response):
    ''' Perform a server-side Google ReCaptcha validation '''
    with requests.post('https://www.google.com/recaptcha/api/siteverify', data={
        "secret": secret,
        "response": response
    }) as req:
        req.raise_for_status()
        if req.json()['success'] != True:
            raise RecaptchaError("Non valid Recaptcha", req.json()['error_codes'])

def post_drupal_contact_message(contact, form_id):
    ''' Post contact message to Drupal '''
    with requests.post(secrets.DRUPAL_CONTACT_MESSAGE_URL, json={
        "contact_form": form_id,
        "message": [contact["message"]],
        "subject": ["Contato - " + contact["name"]],
        "mail": [contact["mail"]],
        "name": [contact["name"]]
    }, auth=(secrets.DRUPAL_AUTH_USER, secrets.DRUPAL_AUTH_PASSWORD)) as req:
        req.raise_for_status()
        return req.json()

@APP.route('/', methods=['POST'])
def handle_form():
    ''' Web entrypoint '''
    try:
        assert request.is_json
        received_data = request.get_json()
        validate(received_data, CONTACT_FORM_SCHEMA)
        do_recaptcha_validation(secrets.RECAPTCHA_SITE_KEY, received_data["recaptcha_response"])
        drupal_response = post_drupal_contact_message(received_data, secrets.DRUPAL_CONTACT_FORM_ID)
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
