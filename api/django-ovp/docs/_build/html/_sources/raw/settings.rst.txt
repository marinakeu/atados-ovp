as ovp is able to serve multiple websites through channel, settings are mostly defined on the database with ChannelSetting model.
If there is no setting with a given key for a channel, ovp will attempt to read it from settings.py, if it's not declared on settings.py, the default setting will be used.

The model
----------
It's a simple key/value model. Keys are not unique, therefore there may be multiple value. Some settings make sense to have multiple value and some may not, if the setting does not support multiple values, the latest record for the channel will be used.


Common settings
-----------------

LANGUAGE_CODE:
Used on: emails.
Todo: use language defined on default django setting

OVP_EMAILS:
Used to: determine if email is enabled or disabled, determine email subject

USER_SEARCH_SERIALIZER
Path to user search serializer!

PROFILE_SERIALIZER_TUPLE
Path to user profile matching (ProfileCreateUpdateSerializer, ProfileRetrieveSerializer, ProfileSearchSerializer)

PROFILE_MODEL
Path to profile model


Converted
___________

CORS_ORIGIN_WHITELIST
=====================
Enable cors for a domain and channel pair.

Type: multi
Example: [("CORS_ORIGIN_WHITELIST", 'domain.com'), ("CORS_ORIGIN_WHITELIST", 'www.domain.com')]
Default: []

CLIENT_URL
=====================
Used on: emails
Type: Single value
Default: ""

MAPS_API_LANGUAGE
=====================
Used to: set maps api language
Type: Single value
Default: "en_US"

EXPIRE_PASSWORD_IN
=====================
Amount of seconds before a password expires and user has to update it.
Password expiration is not enforced on the backend, instead, you'll get a "expired_password" boolean on current user view.
0 should disable.

Type: Single value
Default: "0"

CANT_REUSE_LAST_PASSWORDS
==========================
Disable reuse of last N passwords.
0 should disable

Type: Single value
Default: "0"

ADMIN_MAIL
===========
Admin email.

Type: Single Value
Default: None

UNAUTHENTICATED_APPLY
=====================
Allows unauthenticated applies.

Type: Single value
Default: "0"

CAN_CREATE_PROJECTS_IN_ANY_ORGANIZATION
=======================================
Allows creating projects in any organization

Type: Single Value
Default: "0"

CAN_CREATE_PROJECTS_WITHOUT_ORGANIZATION
=========================================
Allows creating projects without organization

Type: Single Value
Default: "0"

FILTER_OUT_PROJECTS
=======================================
Filter out of project search

Type: Multiple Value
Default: []

FILTER_OUT_ORGANIZATIONS
=======================================
Filter out of organization search

Type: Multiple Value
Default: []
