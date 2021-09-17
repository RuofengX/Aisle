# 导入私有配置
from private import config as private

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
SERVER_PORT = private.SERVER_PORT

# -------Aisle配置-------
VERSION = 'DEV WORK_IN_PROGRESS'
FRP_VERSION = '0.37.1'
TEMP_DIR = './temp'  # 临时文件夹
TLS_DIR = './private/ssl/'  # 处理ssl相关
UID_LENGTH = 5  # uid长度

# -------DEBUG区域-------
LOG_LEVEL = 'DEBUG'  # in ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET']
NO_DEL_TEMP = False  # 启用后将关闭

