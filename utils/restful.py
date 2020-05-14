# -*- coding: utf-8 -*-、
from flask import jsonify


class HttpsCode(object):
    ok = 200
    unautherror = 401
    paramserror = 400
    servererror = 500


def restful_result(code, message, data):
    return jsonify({"code": code, "message": message, "data": data or {}})


def success(message="", data=None):
    return restful_result(code=HttpsCode.ok, message=message, data=data)


def unauth_error(message=""):
    return restful_result(code=HttpsCode.unautherror, message=message, data=None)


def params_error(message=""):
    return restful_result(code=HttpsCode.paramserror, message=message, data=None)


def server_error(message=""):
    return restful_result(code=HttpsCode.servererror, message=message, data=None)
