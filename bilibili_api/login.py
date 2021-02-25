r"""
模块：login
功能：登录功能
项目GitHub地址：https://github.com/bqsgwys/bilibili_api
  _____     ____      _____    ____     
 |  __ \   / __ \   / ____|   / ___\    
 | |__) | | |  | | ( |___    | |      
 |  __ \  | |  | |  \____ \  | | |_ |    
 | |__) | | |_\\ |    ___) | | |__| | 
 |_____/   \___\\   |_____/   \____/            
"""

from . import exceptions, utils
import requests
import json
import qrcode_terminal
from urllib import parse as urlparse
import time

API = utils.get_api()

def print_login_qr_code() -> str:
    """
    获取登录二维码
    :return oauthKey:返回的密钥 
    """
    api = API["login"]["qrcode"]["get_qr_code"]
    ret = utils.get(url=api["url"])
    qrcode_terminal.draw(ret["url"])
    return ret['oauthKey']

def get_qr_code_login_status(oauthKey:str) -> dict    : 
    """
    获取登录信息
    :param oauthKey:登录密钥 
    :return dict:{
        status: 0=success else exception
        verify:Verify格式的cookie
    }
    """
    
    if not (oauthKey):
        raise exceptions.NoIdException
    api = API["login"]["qrcode"]["get_login_info"]
    data = {
        "oauthKey": oauthKey
    }
    try:
        ret = utils.post(url=api["url"],data=data,cookies={})
        cookies = dict(urlparse.parse_qsl(urlparse.urlparse(ret['url']).query))
        return {
            'status': 1,
            'verify': utils.Verify(sessdata = cookies['SESSDATA'], csrf = cookies['bili_jct'])
        }
    except exceptions.BilibiliException as e:
        return {
            'status': e.code,
            'verify': utils.Verify()
        }
    except Exception as e:
        raise e

def qrcode_login(timeout:float = 120) -> utils.Verify:
    """
    自动登录
    STEPS:
        0: POST with oauthKey
        1: if code == true success! else goto 2
        2: if data == -4 goto 0 else goto 5（not scanned yet）
        3: if data == -5 goto 0 & (scanned bot not agree to login) else raise exception(QRcode error)
    :param timeout:手机扫描时间上限，按秒计时
    :return verify:Verify格式的cookie
    """
    startHandleTime = time.time()
    oauthKey = print_login_qr_code()
    status = 0
    while time.time() - startHandleTime < timeout:
        ret = get_qr_code_login_status(oauthKey)
        if ret['status'] == 1:
            return ret['verify']
        elif(ret['status']) == -4:
            if status != -4:
                print('请确认扫描二维码登录')
                status = -4
        elif(ret['status']) == -5:
            if status != -5:
                print('二维码已经扫描，请确认登录')
                status = -5
        else:
            print(ret)
            raise exceptions.QrCodeException
        time.sleep(1)
    raise exceptions.QrCodeTimtoutException
    

