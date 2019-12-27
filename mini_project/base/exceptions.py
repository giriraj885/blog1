from rest_framework.views import exception_handler
from base.views import get_response, BaseAPIView
from rest_framework import exceptions

JWT_ERROR_MESSAGES = {    
    "Authentication credentials were not provided.": "Authentication failed, please re-login.",
    "Signature has expired.": "Authentication failed, please re-login.",
    "Unauthorized user": "Authentication failed, please re-login.",
    "Invalid signature.": "Authentication failed, please re-login.",
    "Incorrect authentication credentials.": "Authentication failed, please re-login."
}

JWT_ERROR_CODE = {
    "Authentication credentials were not provided.": 401,
    "Signature has expired.": 401,
    "Unauthorized user": 401,
    "Invalid signature.": 401,
    "Incorrect authentication credentials.": 401
}

def get_first_error_message(error_dict):
    response = error_dict[next(iter(error_dict))]
    if isinstance(response, dict):
        response = get_first_error_message(response)
    elif isinstance(response, list):
        response = response[0]
        if isinstance(response, dict):
            response = get_first_error_message(response)
    return response

def custom_exception_handler(exc, context):    
    error_response = exception_handler(exc, context)
    error_list = []
    
    if isinstance(exc, exceptions.APIException):
        error_list = get_error_list(exc.get_full_details())
        
        request = context['request']
        request_data = {}
        if request.method == 'GET':
            request_data = request.GET
        else:
            request_data = request.data

        # if 'errors' in error_response.data:
        #     error_list = error_response.data['errors']

        if error_response is not None:
            error = error_response.data
            if isinstance(error, list) and error:
                if isinstance(error[0], dict):
                    error_response.data = get_response(
                        get_first_error_message(error) if not error_list else "",
                        BaseAPIView.FAIL_RESPONSE_STATUS,
                        error_response.status_code,
                        request_data,
                        error_list
                    )
                elif isinstance(error[0], str):
                    error_response.data = get_response(
                        error[0] if not error_list else "",
                        BaseAPIView.FAIL_RESPONSE_STATUS,
                        error_response.status_code,
                        request_data,
                        error_list
                    )

            if isinstance(error, dict):
                error_message = get_first_error_message(error)
                if error_message in JWT_ERROR_MESSAGES:
                    if error_message in JWT_ERROR_CODE:
                        error_response.data = get_response(
                            JWT_ERROR_MESSAGES[error_message] if not error_list else "",
                            BaseAPIView.FAIL_RESPONSE_STATUS,
                            JWT_ERROR_CODE[error_message],
                            request_data,
                            error_list)
                        error_response.status_code = JWT_ERROR_CODE[error_message]
                    else:
                        error_response.data = get_response(
                            JWT_ERROR_MESSAGES[error_message] if not error_list else "",
                            BaseAPIView.FAIL_RESPONSE_STATUS,
                            error_response.status_code,
                            request_data,
                            error_list)
                else:
                    error_response.data = get_response(
                        get_first_error_message(error) if not error_list else "",
                        BaseAPIView.FAIL_RESPONSE_STATUS,
                        error_response.status_code,
                        request_data,
                        error_list
                    )
    return error_response
    
def get_error_list(errors):
    error_list = []
    if isinstance(errors, dict):
        for k, v in errors.items():
            if isinstance(v, list):
                error_list.append(v[0])
            if isinstance(v, dict):
                error_response_list = get_error_list(v)
                for error in error_response_list:
                    error_list.append(error)
    if isinstance(errors, list):
        first_response = errors[0]
        if isinstance(first_response, dict):
            error_list.append(first_response)
            
    return error_list