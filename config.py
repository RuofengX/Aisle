import colorlog
# config.py将被编译到二进制代码中，但会被版本控制同步，请不要存放敏感数据
import dns.resolver
import private  # 模块化的私有参数才能让pyinstaller识别
import random

# -------DEBUG区域-------
LOG_LEVEL = 'INFO'  # in ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET']
NO_DEL_TEMP = False  # 启用后：临时文件夹的文件将不会删除，以供程序运行结束后查看


# -------抽象元类-------
class AisleDefault(object):
    def __init__(self):
        self.logger = colorlog.getLogger(self.__class__.__name__)
        self.logger.setLevel(LOG_LEVEL)
        if not self.logger.handlers:
            self.logger.addHandler(CONSOLE_HANDLER)
        self.logger.debug('日志功能启动')


# -------模块设置-------
# ---logging相关配置---
# 配置着色的Handler
CONSOLE_HANDLER = colorlog.StreamHandler()
CONSOLE_HANDLER.setFormatter(
    colorlog.ColoredFormatter('%(log_color)s%(asctime)s [%(levelname)s] %(name)s(%(funcName)s):\t%(message)s'))
# 配置全局logger
LOG = colorlog.getLogger('GLOBAL')  # 添加全局LOG，避免使用logging.debug()时创建新的handler混淆日志
LOG.setLevel(LOG_LEVEL)
LOG.addHandler(CONSOLE_HANDLER)

# -------AisleCL配置-------
# ---多语言消息实现 | i18n Message---
SPLIT_LINE = '-------------------------------------------'  # split line
INFO = 'OAR Aisle是一个致力于打造沉浸式多人游戏联机体验的软件。'
NAT_TEST_START = '开始NAT-Type测试，请稍等'
NAT_TYPE_IS = '当前网络环境下的NAT-Type为：'
NAT_TYPE_MAP = {"Blocked": "-", "Open Internet": 'SP', "Full Cone": "SSR", "Restrict NAT": "SR",
                "Restrict Port NAT": "R", "Symmetric NAT": "N"}
NAT_HELP = '家庭宽带如抽卡。家宽品质越高，网络连接越容易。一般来说，出现SSR品质则很容易建立连接；而如果出现N品质，则几乎不可能建立连接。'

# ---OAR服务器的私有配置---
SERVER_TOKEN = private.TOKEN
SERVER_DOMAIN = private.SERVER_DOMAIN
try:
    _rrset = dns.resolver.resolve(SERVER_DOMAIN, rdtype='A', raise_on_no_answer=False).rrset
except dns.exception.Timeout:
    LOG.critical(f'无法解析域名，请检查网络连接和DNS服务器配置！')
    raise SystemExit
SERVER_IP = str(_rrset).split(' ')[4]
SERVER_PORT = private.SERVER_PORT

# -------Aisle配置-------
VERSION = 'PRE V1.2.2'
LOG.info(f'版本号{VERSION}')
FRP_VERSION = '0.37.1'  # 兼容的FRP版本
TEMP_DIR_ROOT = './temp'
TEMP_DIR = TEMP_DIR_ROOT + '/' + ''.join(random.sample('1234567890poiuytrewqasdfghjklmnbvcxz', 16))  # # 临时文件夹路径，附加随机一个子文件夹
TLS_DIR = './ssl/'  # ssl证书文件夹路径
UID_LENGTH = 5  # uid长度
DEFAULT_CODEC = 'gbk'
