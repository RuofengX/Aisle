# Aisle的核心
from config import *
import NATTypeDetector
import platform
import os
import subprocess
import logging

# logging相关配置
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s [%(levelname)s] @%(name)s:\t%(message)s'
)


# 自带logger配置
class AisleDefault(object):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(LOG_LEVEL)


class Aisle(AisleDefault):  # 核心控制类，对应vps/主机
    def __init__(self):
        super(Aisle, self).__init__()
        self.logger.info('初始化..')
        self.logger.info('正在测试NAT-Type')
        self.NATType = NATTypeDetector.test()[0]  # 初始化时测试NATType
        self.logger.info('初始化完成')

    def getNATType(self, ifCute=False):
        if ifCute:  # ifCute为真时，使用SSR等抽卡名称
            if self.NATType in NAT_TYPE_MAP.keys():
                natQuality = NAT_TYPE_MAP[self.NATType]
            else:
                natQuality = f"???_{self.NATType}"
            return natQuality
        else:
            return self.NATType

    def startHost(self):
        pass
    # TODO: 使用FrpCtl创建frp的客户端进程


class FrpCtl(AisleDefault):  # 用来创建、控制单个frp进程的类
    def __init__(self, role, args: str):  # role: 暂时仅支持client; args: 形如'xtcp --bind_addr 127.0.0.1' 的字符串
        super(FrpCtl, self).__init__()
        self.logger.info('初始化..')
        # 确定frp相对路径
        system = platform.system().lower()
        arch = platform.architecture()[0][0:2]
        self.binPath = f'./lib/' \
                       f'frp_' \
                       f'{FRP_VERSION}_' \
                       f'{system}_' \
                       f'amd{arch}'
        if role == 'server':
            self.binPath += '/frps'
        elif role == 'client':
            self.binPath += '/frpc'
        self.logger.info(f'使用二进制文件{self.binPath}')

        if os.path.exists(self.binPath):
            pass
        else:
            self.logger.warning(f'没有找到对应的frp文件，frp将无法启动，请联系开发者以获取帮助。检测到的操作系统:{system} {arch}')

        # 确定role为server还是client
        self.role = role
        self.logger.info(f'使用{role}角色')
        if role == 'client':
            self.logger.info('作为服务端启动')
            self.startXTCP()

        # 确定启动参数
        self.args = args

        self.logger.info('初始化完成')

    def startXTCP(self):
        start = [self.binPath] + (self.args.split(' '))
        # TODO: 以特定参数启动XTCP
        '''subprocess.Popen(
            start,
            bufsize=0,
            executable=None,
            stdin=None,
            stdout=None,
            stderr=None,
            preexec_fn=None,
            close_fds=False,
            shell=False,
            cwd=None,
            env=None,
            universal_newlines=False,
            startupinfo=None,
            creationflags=0
        )'''


