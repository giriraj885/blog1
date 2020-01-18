from otslib.utils import helper
from base import constants
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from firebase_admin import messaging
import json

FIREBASE_ADMIN_SDK = 'services/firebase/fire_base_notification.json'
cred = credentials.Certificate(FIREBASE_ADMIN_SDK)
default_app = firebase_admin.initialize_app(cred)
def sendNotification(title, body, data, token):
    """
    @desc: Send notification
    @param: data (dictionary)
        1) title (string)
        2) body (string)
        3) data (dict with any format)
        4) token (string)
    @return:
        Dictionary: {'status' : SUCCESS|FAIL, 'msg' : (string), 'status_code' : (int), data : (dict)}
    """
  
    try:
        notification = messaging.Notification(title=title, body=body)
        web_notification = messaging.WebpushNotification(icon=constants.NOTIFICATION_ICON)
        web_push_config = messaging.WebpushConfig(notification=web_notification)
        message = messaging.Message(
            notification=notification,
            data=data,
            token=token,
            webpush=web_push_config
        )
        message_id = firebase_admin.messaging.send(message)
        return helper.getPositiveResponse("Message send successfully",message_id)
    except Exception as e:
        return helper.getNegativeResponse("Message send failed")