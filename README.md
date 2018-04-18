# Drupal Contact Message Relay

An small API for relaying contact messages from a static page form to Drupal 8, after server-side
Recaptcha validation.

## Environment variables

- RELAY_RECAPTCHA_SECRET_KEY: Google Recaptcha's secret key
- RELAY_DRUPAL_CONTACT_MESSAGE_URL: Drupal rest endpoint for the contact_message entity
- RELAY_DRUPAL_CONTACT_FORM_ID: the contact form id
- RELAY_DRUPAL_AUTH_USER: username allowed to post in the rest endpoint
- RELAY_DRUPAL_AUTH_PASSWORD: password of the user
- RELAY_CORS_ORIGINS: origins to allow access via CORS (default is to allow all origins '*')