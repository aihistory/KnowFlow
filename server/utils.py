import uuid
import base64
import json
from datetime import datetime
from flask import jsonify
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_v1_5
from werkzeug.security import generate_password_hash


# 生成随机的 UUID 作为 id
def generate_uuid():
    return uuid.uuid1().hex

# RSA 加密密码
def rsa_psw(password: str) -> str:
    pub_key = """-----BEGIN PUBLIC KEY-----
    MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEArq9XTUSeYr2+N1h3Afl/z8Dse/2yD0ZGrKwx+EEEcdsBLca9Ynmx3nIB5obmLlSfmskLpBo0UACBmB5rEjBp2Q2f3AG3Hjd4B+gNCG6BDaawuDlgANIhGnaTLrIqWrrcm4EMzJOnAOI1fgzJRsOOUEfaS318Eq9OVO3apEyCCt0lOQK6PuksduOjVxtltDav+guVAA068NrPYmRNabVKRNLJpL8w4D44sfth5RvZ3q9t+6RTArpEtc5sh5ChzvqPOzKGMXW83C95TxmXqpbK6olN4RevSfVjEAgCydH6HN6OhtOQEcnrU97r9H0iZOWwbw3pVrZiUkuRD1R56Wzs2wIDAQAB
    -----END PUBLIC KEY-----"""

    rsa_key = RSA.import_key(pub_key)
    cipher = PKCS1_v1_5.new(rsa_key)
    encrypted_data = cipher.encrypt(base64.b64encode(password.encode()))
    return base64.b64encode(encrypted_data).decode()

# 加密密码
def encrypt_password(raw_password: str) -> str:
    base64_password = base64.b64encode(raw_password.encode()).decode()
    return generate_password_hash(base64_password)

# 自定义JSON序列化器，处理datetime对象
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return super().default(obj)

# 标准响应格式
def success_response(data=None, message="操作成功", code=0):
    response = {
        "code": code,
        "message": message,
        "data": data
    }
    # 使用自定义的JSON序列化器
    json_str = json.dumps(response, cls=DateTimeEncoder, ensure_ascii=False)
    return json_str, 200, {'Content-Type': 'application/json; charset=utf-8'}

# 错误响应格式
def error_response(message="操作失败", code=500, details=None):
    """标准错误响应格式"""
    response = {
        "code": code,
        "message": message
    }
    if details:
        response["details"] = details
    json_str = json.dumps(response, cls=DateTimeEncoder, ensure_ascii=False)
    return json_str, code if code >= 400 else 500, {'Content-Type': 'application/json; charset=utf-8'}