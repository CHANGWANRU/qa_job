import json  #将请求参数转为 JSON 字符串，用于日志和 allure 附件
import allure
import pytest
import requests  #发送 HTTP 请求
import urllib3 #禁用 SSL 警告时使用
import time

from conf import setting  #读取配置，如 API_TIMEOUT 超时时间
from common.recordlog import logs
from requests import utils
from common.readyaml import ReadYamlData
from requests.packages.urllib3.exceptions import InsecureRequestWarning #忽略 HTTPS 证书验证警告


class SendRequest:
    """发送接口请求，暂时只写了get和post方法的请求"""

    def __init__(self, cookie=None):
        self.cookie = cookie  #给当前对象创建一个属性，名字叫 cookie
        self.read = ReadYamlData() #给当前对象创建另一个属性，名字叫 read，生成一个 ReadYamlData 类型的对象，然后把它赋给 self.read

    def get(self, url, data, header):
        """
        :param url: 接口地址
        :param data: 请求参数
        :param header: 请求头
        :return:
        """
        requests.packages.urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) #禁用 SSL 警告
        try:
            if data is None:
                response = requests.get(url, headers=header, cookies=self.cookie, verify=False)
            else:
                response = requests.get(url, data, headers=header, cookies=self.cookie, verify=False)
        except requests.RequestException as e:  #捕获所有 requests 相关异常，记录日志并返回 None。
            logs.error(e)
            return None
        except Exception as e:
            logs.error(e)
            return None
        # 响应时间/毫秒
        res_ms = response.elapsed.microseconds / 1000
        # 响应时间/秒
        res_second = response.elapsed.total_seconds()

        response_dict = dict()
        # 接口响应状态码
        response_dict['code'] = response.status_code
        # 接口响应文本
        response_dict['text'] = response.text
        try:
            response_dict['body'] = response.json().get('body')
        except Exception:
            response_dict['body'] = ''
        response_dict['res_ms'] = res_ms
        response_dict['res_second'] = res_second
        return response_dict

    def post(self, url, data, header):
        """
        :param url:
        :param data: verify=False忽略SSL证书验证
        :param header:
        :return:
        """
        # 控制台输出InsecureRequestWarning错误
        requests.packages.urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        try:
            if data is None:
                response = requests.post(url, header, cookies=self.cookie, verify=False)
            else:
                response = requests.post(url, data, headers=header, cookies=self.cookie, verify=False)
        except requests.RequestException as e:
            logs.error(e)
            return None
        except Exception as e:
            logs.error(e)
            return None
        # 响应时间/毫秒
        res_ms = response.elapsed.microseconds / 1000
        # 响应时间/秒
        res_second = response.elapsed.total_seconds()
        response_dict = dict()
        # 接口响应状态码
        response_dict['code'] = response.status_code
        # 接口响应文本
        response_dict['text'] = response.text
        try:
            response_dict['body'] = response.json().get('body')
        except Exception:
            response_dict['body'] = ''
        response_dict['res_ms'] = res_ms
        response_dict['res_second'] = res_second
        return response_dict

   #通用的 HTTP 请求发送器，根据传入的 **kwargs 参数（方法、URL、请求头、数据等）发送请求
    def send_request(self, **kwargs):  #**kwargs：关键字参数，这意味着你可以传入任意多个参数名和值

        session = requests.session() #创建一个会话对象，可以自动保持 Cookie
        result = None
        cookie = {}  #准备一个字典，用于存放从响应中提取的 cookie
        try:
            result = session.request(**kwargs)
            set_cookie = requests.utils.dict_from_cookiejar(result.cookies)
            if set_cookie:
                cookie['Cookie'] = set_cookie
                self.read.write_yaml_data(cookie)
                logs.info("cookie：%s" % cookie)
            logs.info("接口返回信息：%s" % result.text if result.text else result)
        except requests.exceptions.ConnectionError:
            logs.error("ConnectionError--连接异常")
            pytest.fail("接口请求异常，可能是request的连接数过多或请求速度过快导致程序报错！")
        except requests.exceptions.HTTPError:
            logs.error("HTTPError--http异常")
        except requests.exceptions.RequestException as e:
            logs.error(e)
            pytest.fail("请求异常，请检查系统或数据是否正常！")
        return result
    #最终统一入口
    def run_main(self, name, url, case_name, header, method, cookies=None, file=None, **kwargs):
        """
        接口请求
        :param name: 接口名
        :param url: 接口地址
        :param case_name: 测试用例
        :param header:请求头
        :param method:请求方法
        :param cookies：默认为空
        :param file: 上传文件接口
        :param kwargs: 请求参数，根据yaml文件的参数类型
        :return:
        """

        try:
            # 收集报告日志
            logs.info('接口名称：%s' % name)
            logs.info('请求地址：%s' % url)
            logs.info('请求方式：%s' % method)
            logs.info('测试用例名称：%s' % case_name)
            logs.info('请求头：%s' % header)
            logs.info('Cookie：%s' % cookies)
            req_params = json.dumps(kwargs, ensure_ascii=False)  #处理请求参数
    #根据参数类型添加 Allure 附件
            if "data" in kwargs.keys():
                allure.attach(req_params, '请求参数', allure.attachment_type.TEXT)
                logs.info("请求参数：%s" % kwargs)
            elif "json" in kwargs.keys():
                allure.attach(req_params, '请求参数', allure.attachment_type.TEXT)
                logs.info("请求参数：%s" % kwargs)
            elif "params" in kwargs.keys():
                allure.attach(req_params, '请求参数', allure.attachment_type.TEXT)
                logs.info("请求参数：%s" % kwargs)
        except Exception as e:
            logs.error(e)
        # time.sleep(0.5)
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  #禁用 SSL 警告
        response = self.send_request(method=method,
                                     url=url,
                                     headers=header,
                                     cookies=cookies,
                                     files=file,
                                     timeout=setting.API_TIMEOUT,
                                     verify=False,
                                     **kwargs)
        return response  #返回 send_request 的结果（Response 对象或异常时的 None
