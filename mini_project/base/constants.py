EXCEPTION_RESPONSE_CODE = {
    "Authentication credentials were not provided." : 401,
    "Signature has expired." : 401,
    "Unauthorized user" : 401,
    "Invalid signature." : 401,
    "Incorrect authentication credentials."  : 401
}

EXCEPTION_HANDLER = {
    "user with this email already exists." : "User already exist with this email",
    "Unauthorized user" : "Unauthorized user",
    "Upload a valid image. The file you uploaded was either not an image or a corrupted image." : "Upload a valid image. The file you uploaded was either not an image or a corrupted image.",
    "Authentication credentials were not provided." : "Authentication failed, please re-login.",
    "Signature has expired." : "Authentication failed, please re-login.",
    "Unauthorized user" : "Authentication failed, please re-login.",
    "Invalid signature." : "Authentication failed, please re-login.",
    "Incorrect authentication credentials."  : "Authentication failed, please re-login."
}

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
USER_PER_PAGE = 20
NO_USER_IMAGE = 'https://images-na.ssl-images-amazon.com/images/I/61Krpl7FGyL._SX425_.jpg'

NOTIFICATION_ICON="https://img.icons8.com/bubbles/2x/appointment-reminders.png"