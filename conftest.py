# -*- coding: utf-8 -*-
import time

import pytest

from common.readyaml import ReadYamlData  #是一个类，用于读取和操作 YAML 文件（包括清理 extract.yaml）。
from base.removefile import remove_file #函数，用于删除指定目录下的特定后缀文件。
from common.dingRobot import send_dd_msg #钉钉机器人发送消息的函数
from conf.setting import dd_msg  #配置变量，控制是否发送钉钉消息（布尔值）

import warnings #Python 内置的警告模块。

yfd = ReadYamlData()  #创建一个全局对象 yfd，用来操作 YAML 文件（例如清理 extract.yaml 中的数据）

#每次运行测试前，清理环境，确保没有残留数据。
@pytest.fixture(scope="session", autouse=True) #autouse=True,不用测试函数把函数名写进形参，所有的测试用例都会自动执行
def clear_extract():
    # 禁用HTTPS告警，ResourceWarning
    warnings.simplefilter('ignore', ResourceWarning)  #忽视资源警告

    yfd.clear_yaml_data()  #清空 extract.yaml 文件中的内容，不能让上次过期的token影响了这次的运行呀
    remove_file("./report/temp", ['json', 'txt', 'attach', 'properties']) #：删除 ./report/temp 目录下所有后缀为 json、txt、attach、properties 的文件（这些是 Allure 运行时生成的临时文件，每次运行前清理，避免旧数据干扰）


def generate_test_summary(terminalreporter): #terminalreporter 是 pytest 内置的插件对象，包含测试运行的统计信息
    """生成测试结果摘要字符串"""
    total = terminalreporter._numcollected
    passed = len(terminalreporter.stats.get('passed', []))
    failed = len(terminalreporter.stats.get('failed', []))
    error = len(terminalreporter.stats.get('error', []))
    skipped = len(terminalreporter.stats.get('skipped', []))
    duration = time.time() - terminalreporter._sessionstarttime

    summary = f"""
    自动化测试结果，通知如下，请着重关注测试失败的接口，具体执行结果如下：
    测试用例总数：{total}
    测试通过数：{passed}
    测试失败数：{failed}
    错误数量：{error}
    跳过执行数量：{skipped}
    执行总时长：{duration}
    """
    print(summary)
    return summary

#这是 pytest 内置的钩子，在所有测试执行完毕，终端输出摘要之前自动调用
def pytest_terminal_summary(terminalreporter, exitstatus, config): #这里的参数都是pytest内置的参数
    """自动收集pytest框架执行的测试结果并打印摘要信息"""
    summary = generate_test_summary(terminalreporter)
    if dd_msg:
        send_dd_msg(summary)
