import allure
import pytest

from common.readyaml import get_testcase_yaml
from base.apiutil_business import RequestBase #业务场景专用请求基类，内部会处理 YAML 中的占位符、提取变量、发送请求等。这是核心执行器。
from base.generateId import m_id, c_id #生成唯一 ID 的函数


# 注意：业务场景的接口测试要调用base目录下的apiutil_business文件

@allure.feature(next(m_id) + '电子商务管理系统（业务场景）') #在 Allure 报告中创建一个大的模块分类
class TestEBusinessScenario:

    @allure.story(next(c_id) + '商品列表到下单支付流程')
    @pytest.mark.parametrize('case_info', get_testcase_yaml('./testcase/Business interface/BusinessScenario.yml')) #get_testcase_yaml 会直接返回原始 data（即包含 5 个元素的列表，每个元素是一个字典，包含 baseInfo 和 testCase）。
    def test_business_scenario(self, case_info):
        allure.dynamic.title(case_info['baseInfo']['api_name']) #动态设置 Allure 报告中当前测试用例的标题，显示为接口名称（如 "商品列表"、"商品详情"）
        RequestBase().specification_yaml(case_info)
