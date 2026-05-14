import yaml
import traceback #Python 内置库，用于打印详细的异常堆栈信息
import os  #内置库，用于文件和路径操作

from common.recordlog import logs #导入自定义的日志记录器（logs 对象），用于输出错误信息到日志文件或控制台
from conf.operationConfig import OperationConfig #导入配置类，可能用于读取操作配置（如环境、超时等）
from conf.setting import FILE_PATH #字典，里面定义了重要文件的路径，例如 'EXTRACT' 对应的路径就是 extract.yaml 的完整路径
from yaml.scanner import ScannerError

 #专门用于解析测试用例 YAML 文件（例如 getProductList.yaml），并将文件内容转换成一种方便参数化的数据结构
def get_testcase_yaml(file):
    testcase_list = []  #创建一个空列表，用来存储处理后的测试用例数据。
    try:
        with open(file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)  #将 YAML 文件内容解析为 Python 对象（通常是列表或字典）
            if len(data) <= 1:
                yam_data = data[0] #取出列表的第一个元素（也是唯一的元素），这个元素是一个字典，包含 baseInfo 和 testCase
                base_info = yam_data.get('baseInfo')  #why不直接yam_data['basseinfo'],为啥还用一个get函数
                for ts in yam_data.get('testCase'):
                    param = [base_info, ts]  #组成一个二元列表，也就是接口信息和单个用例组成的列表
                    testcase_list.append(param)  #将这个二元列表添加到 testcase_list 中。
                return testcase_list  #处理后的列表为[ [baseInfo字典, testCase1字典] , [baseInfo字典, testCase1字典],.....]
            else:
                return data #说明文件可能包含多个独立的接口配置（每个都有自己的 baseInfo 和 testCase），就直接返回原始数据，让调用方自己处理
    except UnicodeDecodeError: #编码错误（文件不是 UTF-8），记录日志并隐式返回 None
        logs.error(f"[{file}]文件编码格式错误，--尝试使用utf-8编码解码YAML文件时发生了错误，请确保你的yaml文件是UTF-8格式！")
    except FileNotFoundError: #文件不存在，记录日志
        logs.error(f'[{file}]文件未找到，请检查路径是否正确')
    except Exception as e: #其他任何异常，记录日志并打印异常信息
        logs.error(f'获取【{file}】文件数据时出现未知错误: {str(e)}')


class ReadYamlData:
    """读写接口的YAML格式测试数据"""

    def __init__(self, yaml_file=None): #Python 类中的一个特殊方法，来初始化这个新对象，相当于c++的构造函数
        if yaml_file is not None:
            self.yaml_file = yaml_file  #self 是 __init__ 方法的第一个参数，它代表正在被创建的那个对象本身
        else:
            pass
        self.conf = OperationConfig() #创建一个 OperationConfig 类的对象，并赋值给当前对象的 conf 属性
        self.yaml_data = None #给当前对象创建一个 yaml_data 属性，并初始化为 None，以后可能用来存储从 YAML 文件读取的数据

    @property #将方法变成属性调用，不需要加括号。例如 obj.get_yaml_data 会执行这个方法并返回结果
    def get_yaml_data(self):
        """
        获取测试用例yaml数据
        :param file: YAML文件
        :return: 返回list
        """
        # Loader=yaml.FullLoader表示加载完整的YAML语言，避免任意代码执行，无此参数控制台报Warning
        try:
            with open(self.yaml_file, 'r', encoding='utf-8') as f:
                self.yaml_data = yaml.safe_load(f)  #读取 self.yaml_file 指定的 YAML 文件，返回解析后的数据，同时缓存到 self.yaml_data
                return self.yaml_data
        except Exception:
            logs.error(str(traceback.format_exc()))

#将数据追加写入 extract.yaml 文件，用于保存接口返回的变量（如 token、订单号等），供后续用例使用
    def write_yaml_data(self, value):
        """
        写入数据需为dict，allow_unicode=True表示写入中文，sort_keys按顺序写入
        写入YAML文件数据,主要用于接口关联
        :param value: 写入数据，必须用dict
        :return:
        """

        file = None
        file_path = FILE_PATH['EXTRACT'] #从配置中获取 extract.yaml 的完整路径
        if not os.path.exists(file_path):
            os.system(file_path)
        try:
            file = open(file_path, 'a', encoding='utf-8') #以追加模式a打开文件。追加意味着每次写入不会覆盖之前的内容，而是在文件末尾添加
            if isinstance(value, dict): #只允许写入字典类型的数据
                write_data = yaml.dump(value, allow_unicode=True, sort_keys=False) #yaml.dump：将 Python 字典转换成 YAML 格式的字符串
                file.write(write_data) #将 YAML 字符串写入文件
            else:
                logs.info('写入[extract.yaml]的数据必须为dict格式')
        except Exception:
            logs.error(str(traceback.format_exc()))
        finally:
            file.close()

    def clear_yaml_data(self):
        """
        清空extract.yaml文件数据
        :param filename: yaml文件名
        :return:
        """
        with open(FILE_PATH['EXTRACT'], 'w') as f: #以写入模式 'w' 打开 extract.yaml，这会清空文件内容（因为 'w' 会截断文件）
            f.truncate()  #截断文件到当前文件指针位置（刚打开时指针在开头，所以相当于清空），但实际上上一步已经清空了

    #从 extract.yaml 中读取之前写入的变量值，支持一级或二级节点
    def get_extract_yaml(self, node_name, second_node_name=None):
        """
        用于读取接口提取的变量值
        :param node_name:
        :return:
        """
        if os.path.exists(FILE_PATH['EXTRACT']):
            pass
        else:
            logs.error('extract.yaml不存在')
            file = open(FILE_PATH['EXTRACT'], 'w')
            file.close()
            logs.info('extract.yaml创建成功！')
        try:
            with open(FILE_PATH['EXTRACT'], 'r', encoding='utf-8') as rf:
                ext_data = yaml.safe_load(rf)
                if second_node_name is None:
                    return ext_data[node_name]
                else:
                    return ext_data[node_name][second_node_name]
        except Exception as e:
            logs.error(f"【extract.yaml】没有找到：{node_name},--%s" % e)

    def get_testCase_baseInfo(self, case_info):
        """
        获取testcase yaml文件的baseInfo数据
        :param case_info: yaml数据，dict类型
        :return:
        """
        pass

    def get_method(self):
        """
        :param self:
        :return:
        """
        yal_data = self.get_yaml_data()
        metd = yal_data[0].get('method')
        return metd

    def get_request_parame(self):
        """
        获取yaml测试数据中的请求参数
        :return:
        """
        data_list = [] #创建一个空列表
        yaml_data = self.get_yaml_data()
        del yaml_data[0]  #删除第一个元素（可能是 baseInfo）
        for da in yaml_data:
            data_list.append(da)
        return data_list
