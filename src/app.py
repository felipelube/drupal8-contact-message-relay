'''
An small API for relaying contact messages to Drupal after server-side Recaptcha validation.
'''
from exceptions import RecaptchaError, APIException
from jsonschema import ValidationError, validate
from flask import Flask, jsonify, json, request
from flask_cors import CORS, cross_origin
from flask_env import MetaFlaskEnv
import requests
import schemas
import logging
import jsend
import sys


APP = Flask(__name__)


class Configuration(metaclass=MetaFlaskEnv):
    ENV_PREFIX = 'RELAY_'

    RECAPTCHA_SECRET_KEY = ''
    DRUPAL_CONTACT_MESSAGE_URL = ''
    DRUPAL_CONTACT_FORM_ID = ''
    DRUPAL_AUTH_USER = ''
    DRUPAL_AUTH_PASSWORD = ''
    CORS_ORIGINS = "*"
    # use the Drupal 8 schema for backwards compatibility
    SELECTED_SCHEMA = 'CONTACT_FORM_SCHEMA'


APP.config.from_object(Configuration)
CORS(app=APP, origins=APP.config['CORS_ORIGINS'])

# quit early if the user selected schema is not defined in the built-in schemas
try:
    SELECTED_SCHEMA = getattr(schemas, APP.config['SELECTED_SCHEMA'])
except AttributeError:
    raise ValueError(
        "The selected schema does not exist in the built-in schemas")


def do_recaptcha_validation(response):
    ''' Perform a server-side Google ReCaptcha validation '''
    with requests.post('https://www.google.com/recaptcha/api/siteverify', data={
        "secret": APP.config["RECAPTCHA_SECRET_KEY"],
        "response": response
    }) as req:
        try:
            req.raise_for_status()
            json_response = req.json()
            if not getattr(json_response, 'success', False):
                raise ValueError()
        except ValueError:
            raise RecaptchaError("Invalid", json_response['error-codes'])
        except requests.exceptions.RequestException:
            raise APIException("Failed to connect to ReCaptcha Service", 503)
        except:
            raise APIException("Server error", 500)
        else:
            return True


def post_drupal_contact_message(contact):
    ''' Post contact message to Drupal '''
    with requests.post(APP.config["DRUPAL_CONTACT_MESSAGE_URL"], json={
        "contact_form": APP.config["DRUPAL_CONTACT_FORM_ID"],
        "message": [contact["message"]],
        "subject": ["Contato - " + contact["name"]],
        "mail": [contact["mail"]],
        "name": [contact["name"]]
    }, auth=(APP.config["DRUPAL_AUTH_USER"], APP.config["DRUPAL_AUTH_PASSWORD"])) as req:
        try:
            req.raise_for_status()
        except:
            raise APIException("Failed to connect to Drupal", 503)
        else:
            return req.json()


@APP.route('/', methods=['POST'])
def handle_form():
    ''' Web entrypoint '''
    try:
        if not request.is_json:
            raise ValueError()
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
    except (RecaptchaError, ValidationError, ValueError):
        raise APIException("Invalid captcha or bad request")
    except:
        raise APIException("Server error", 500)


@APP.errorhandler(APIException)
def handle_api_exception(error):
    '''Global error handler'''
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    logging.exception(error)
    return response
