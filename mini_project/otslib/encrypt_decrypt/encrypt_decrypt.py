import logging
import os
from Crypto.Cipher import AES

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

def decryptDict(mdict):

    decrypted_dict = mdict

    for key, value in mdict.iteritems():
        decrypted_dict[key] = decrypt(getSecretKey(), value, True)

    return decrypted_dict

def encryptDict(mdict):

    encrypted_dict = mdict

    for key, value in mdict.iteritems():
        encrypted_dict[key] = encrypt(getSecretKey(), value, True)

    return encrypted_dict


def encryptListOfDict(gateway_parameter_list):

    encrypt_gateway_parameter_list = []
    for payment_gateway in gateway_parameter_list:
        encrypt_gateway_parameter_list.append(encryptDict(payment_gateway))

    return encrypt_gateway_parameter_list


def decryptListOfDict(gateway_parameter_list):

    decrypt_gateway_parameter_list = []
    for payment_gateway in gateway_parameter_list:
        decrypt_gateway_parameter_list.append(decryptDict(payment_gateway))

    return decrypt_gateway_parameter_list
