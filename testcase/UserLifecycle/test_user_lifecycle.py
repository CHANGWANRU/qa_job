import allure
import pytest

from common.readyaml import get_testcase_yaml
from base.apiutil_business import RequestBase
from base.generateId import m_id, c_id


@allure.feature(next(m_id) + '用户生命周期管理（业务场景）')
class TestUserLifecycle:

    @allure.story(next(c_id) + '登录→新增→查询→修改→查证→删除')
    @pytest.mark.parametrize(
        'case_info',
        get_testcase_yaml('./testcase/UserLifecycle/user_lifecycle.yaml')
    )
    def test_user_lifecycle(self, case_info):
        allure.dynamic.title(case_info['baseInfo']['api_name'])
        RequestBase().specification_yaml(case_info)