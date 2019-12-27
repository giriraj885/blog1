from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import AllowAny
from base.authentication import CustomAuthentication
from rest_framework.serializers import ValidationError 
import string
import random
from Crypto.Cipher import AES
import os

RECORDS_PER_PAGE = 10

def get_response(msg, status=True, statusCode=200, result=None, errorList=[]):
    response = {}
    response['status'] = status
    response['message'] = msg
    response['result'] = result
    response['statusCode'] = statusCode
    response['error'] = errorList
    return response

def randomGeneratorCode(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

def getSecretKey():
    return str.encode('p2#$1m#@92W!Qqa&', 'utf-8')

def getSaltSize():
    return 32

def getblockSize():
    return 16

def getAESMode():
    return AES.MODE_CBC

def encrypt(password, plaintext, base64=False):

    BLOCK = getblockSize()
    SALT = getSaltSize()
    MODE = getAESMode()

    salt = os.urandom(SALT)
    iv = os.urandom(BLOCK)

    secret_key = password

    cipher_spec = AES.new(secret_key, MODE, iv)

    paddingLength = 16 - (len(str(plaintext)) % 16)
    paddedPlaintext = str(plaintext) + ' ' * paddingLength

    ciphertext = cipher_spec.encrypt(str.encode(paddedPlaintext, 'utf-8'))
    ciphertext = ciphertext + iv + salt

    if base64:
        import base64
        return (base64.b64encode(ciphertext)).decode("utf-8")
    else:
        return ciphertext.encode("hex")


def decrypt(password, ciphertext, base64=False):

    BLOCK = getblockSize()
    SALT = getSaltSize()
    MODE = getAESMode()

    if base64:
        import base64
        decodedCiphertext = base64.b64decode(ciphertext)
    else:
        decodedCiphertext = ciphertext.decode("hex")

    startIv = len(decodedCiphertext) - BLOCK - SALT
    startSalt = len(decodedCiphertext) - SALT

    data, iv, salt = decodedCiphertext[:startIv], decodedCiphertext[startIv:startSalt], decodedCiphertext[startSalt:]

    derivedKey = password
    cipherSpec = AES.new(derivedKey, MODE, iv)
    plaintextWithPadding = cipherSpec.decrypt(data)
    plaintext = plaintextWithPadding.decode('utf8').rstrip(' ')

    return plaintext


class BaseAPIView(APIView):
    
    FAIL_RESPONSE_STATUS = False
    PASS_RESPONSE_STATUS = True
    SUCCESS_CODE = 200
    BLANK_MSG = ''

    # GENERIC PAGINATION METHOD
    def get_paginated_records(self, request, records):
        
        records_per_page = RECORDS_PER_PAGE
        total_pages = 0
        page_start = 0
        page_end = 0

        if 'page_no' in request.GET and request.GET['page_no'] != '0':
            page_end = int(request.GET['page_no']) * records_per_page
            page_start = page_end - records_per_page
        elif 'page_no' in request.data and request.data['page_no'] != '0':
            page_end = int(request.data['page_no']) * records_per_page
            page_start = page_end - records_per_page
        else:
            page_end = records_per_page

        total_records_count = records.count()

        records_remainder = records.count() % records_per_page
        total_pages = int(total_records_count/records_per_page)
        if records_remainder != 0:
            total_pages += 1

        records = records[page_start:page_end]
        response_data = {
            "total_pages": total_pages,
            "total_records_count": total_records_count,
            "records": records,
            "items_per_page": RECORDS_PER_PAGE
        }
        return response_data

    # GENRIC METHOD FOR ERROR HANDLING
    def getErrorResponse(self, serializer, status_code):
        return


