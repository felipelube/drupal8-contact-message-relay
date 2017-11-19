'''
JSON Schemas used in this API
'''
CONTACT_FORM_SCHEMA = {
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
