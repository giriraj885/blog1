from base import constants
from rest_framework.views import exception_handler
from otslib.utils import helper

def custom_exception_handler(exc, context):

    error_response = exception_handler(exc, context)
    if error_response is not None:
        error = error_response.data
        if isinstance(error, list) and error:
            if isinstance(error[0], dict):
                error_response.data = helper.getNegativeResponse(
                        helper.getErrorMessage(error), 
                        error_response.status_code
                    )

            elif isinstance(error[0], str):
                error_response.data = helper.getNegativeResponse(
                        error[0],
                        error_response.status_code
                    )

        if isinstance(error, dict):
            error_message = helper.getFirstErrorMessage(error)
            if error_message in constants.EXCEPTION_HANDLER:
                if error_message in constants.EXCEPTION_RESPONSE_CODE:
                    error_response.data = helper.getNegativeResponse(constants.EXCEPTION_HANDLER[error_message], constants.EXCEPTION_RESPONSE_CODE[error_message])
                    error_response.status_code = constants.EXCEPTION_RESPONSE_CODE[error_message]
                else:
                    error_response.data = helper.getNegativeResponse(constants.EXCEPTION_HANDLER[error_message], error_response.status_code)
            else:
                error_response.data = helper.getNegativeResponse(
                        helper.getErrorMessage(error), 
                        error_response.status_code
                    )

    return error_response