# config.py将被编译到二进制代码中，但会被版本控制同步，请不要存放敏感数据
import dns.resolver
import private  # 模块化的私有参数才能让pyinstaller识别

# -------AisleCL配置-------
# 多语言消息实现 | i18n Message
INFO = 'OAR Aisle是一个致力于打造沉浸式多人游戏联机体验的软件。'
NAT_TEST_START = '开始NAT-Type测试，请稍等'
NAT_TYPE_IS = '当前网络环境下的NAT-Type为：'
NAT_TYPE_MAP = {"Blocked": "-", "Open Internet": 'SP', "Full Cone": "SSR", "Restrict NAT": "SR",
                "Restrict Port NAT": "R", "Symmetric NAT": "N"}
NAT_HELP = '家庭宽带如抽卡。家宽品质越高，网络连接越容易。一般来说，出现SSR品质则很容易建立连接；而如果出现N品质，则几乎不可能建立连接。'

# OAR服务器的私有配置
TOKEN = private.TOKEN
SERVER_DOMAIN = private.SERVER_DOMAIN
_rrset = dns.resolver.resolve(SERVER_DOMAIN, rdtype='A', raise_on_no_answer=False).rrset
SERVER_IP = str(_rrset).split(' ')[4]
SERVER_PORT = private.SERVER_PORT

# -------Aisle配置-------
VERSION = 'PRE V1.0.0'
FRP_VERSION = '0.37.1'  # 兼容的FRP版本
TEMP_DIR = './temp'  # 临时文件夹路径
TLS_DIR = './ssl/'  # ssl证书文件夹路径
UID_LENGTH = 5  # uid长度


# -------DEBUG区域-------
LOG_LEVEL = 'INFO'  # in ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET']
NO_DEL_TEMP = False  # 启用后：临时文件夹的文件将不会删除，以供程序运行结束后查看
