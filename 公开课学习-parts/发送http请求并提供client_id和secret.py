# 在处理HTTP请求时，尤其是在涉及到需要认证的API时，client_id 和 secret 是常见术语，特别是在OAuth 2.0认证流程中。下面我将详细解释这两个术语的含义以及它们如何在实践中使用。
# 
# 1. Client ID 和 Secret
# 
# Client ID：
# 
# 定义：Client ID 是客户端应用程序的身份标识。它是开发者在注册应用程序时从服务提供商（如Google, Facebook, Twitter等）获得的唯一标识符。
# 用途：在OAuth 2.0流程中，Client ID用于标识应用程序，以便服务提供商可以验证请求的来源。
# 
# Secret：
# 
# 定义：Secret（也称为Client Secret）是与Client ID一起提供的密钥，用于增强安全性。它是为了防止未经授权的第三方访问你的应用程序的身份信息。
# 用途：在OAuth 2.0流程中，Secret用于验证请求的合法性，通常在生成授权码或访问令牌时使用。
# 
# 2. 使用 Client ID 和 Secret
# 在HTTP请求中，尤其是在进行OAuth 2.0认证时，你通常需要通过以下几种方式之一来提供client_id和secret：
# 
# 往往是 HTTP Basic Auth
# 在这种方法中，你需要在HTTP请求的头部使用Basic Auth来发送client_id和secret。
# 
# http
# Copy Code
# Authorization: Basic <base64_encoded_client_id:client_secret>

import datetime
import requests
import json
import sys

import base64
import hashlib
import hmac
import time

request = { # 一个字典，不是json
    "pointIdInMapless": "1959067062614327347",
    "pointIdInHdmap": "1981242691845034034",
    "mapVersion": "shenzhen_admap_v5.152.0.r",
    "useBinary": True,
}

def get_auth_data(timestamp, client_secret, url_path, http_method):
    string_to_sign = "%s %s\n%s" % (http_method, url_path, timestamp)
    hmac_bytes = hmac.new(
        bytes(client_secret.encode("ascii")),
        bytes(string_to_sign.encode("ascii")),
        hashlib.sha1,
    ).digest()
    auth = base64.b64encode(hmac_bytes).decode("utf-8")
    return auth


def create_headers(client_id, client_secret, url_path, http_method):
    timestamp = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
    auth = get_auth_data(timestamp, client_secret, url_path, http_method)
    return {
        "Date": timestamp,
        "Authorization": "MWS %s:%s" % (client_id, auth),
        "Content-Type": "application/json;charset=utf-8",
    }

def queryMemoryRoute(env, request, print_log=True):
    URI = '/query/memory/route'
    URL_TEST = 'http://walledata.mad.test.sankuai.com/autodrive/service' + URI
    URL_STAGING = 'https://autodrive.adp.st.sankuai.com' + URI
    if print_log:
        print(request)
    if env == "test":
        headers = create_headers('xxxx', 'xxxxxxxx', URI, 'GET') # 有些要改用 'POST'
        response = requests.get(URL_TEST, params=request, headers=headers) # 这里也改用post
        if print_log:
            print("test response: ", response.text)
        return json.loads(response.text)
    elif env == "staging":
        headers = create_headers('yyyy', 'yyyyyyyy', URI, 'GET')
        response = requests.get(URL_STAGING, params=request, headers=headers)
        if print_log:
            print("staging response: ", response.text)
        return json.loads(response.text)
