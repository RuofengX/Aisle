# Aisle的核心
from config import *
import NATTypeDetector
import platform
import os
import logging
from subprocess import Popen, PIPE, STDOUT
import chardet
import shortuuid
from socket import gethostname
import _thread as thread
from base64 import b64encode, b64decode
from time import sleep

# logging相关配置
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s [%(levelname)s] @%(name)s:\t%(message)s'
)


# 使用logging记录subprocess的输出，来自 https://stackoverflow.com/questions/21953835/run-subprocess-and-print-output-to-logging
def logSubprocessOutput(pipe, logger):
    codec = chardet.detect(pipe.readline(12))['encoding']  # 获取编码方式
    for line in iter(pipe.readline, b''):
        line = line.decode(codec).replace('\n', '')  # 删去行末的/n，logging自动会换行
        logger.info(line)


# 自带logger配置
class AisleDefault(object):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(LOG_LEVEL)


class Aisle(AisleDefault):  # 核心控制类，对应vps/主机
    def __init__(self):
        super(Aisle, self).__init__()
        self.logger.info('初始化..')

        self.logger.info('初始化参数...')
        self.NATType = NATTypeDetector.test()[0]
        self.mode = ''
        self.xtcp = None

        self.logger.info('正在测试NAT-Type')
        # self.NATType = NATTypeDetector.test()[0]
        self.logger.info(f'NAT-Type为：{self.NATType}')

        self.logger.info('初始化完成')

    def getNATType(self, ifCute=False):
        self.NATType = NATTypeDetector.test()[0]  # 进行一次NAT测试
        if ifCute:  # ifCute为真时，使用SSR等抽卡名称
            if self.NATType in NAT_TYPE_MAP.keys():
                natQuality = NAT_TYPE_MAP[self.NATType]
            else:
                natQuality = f"???_{self.NATType}"
            return natQuality
        else:
            return self.NATType

    def startXTCPHost(self, serverAddr, token, sk, localPort):
        self.mode = 'XTCP'
        self.xtcp = XTCP(serverAddr=serverAddr, token=token)
        thread.start_new_thread(self.xtcp.startHost, (sk, localPort))  # 实用新线程启动外部程序
        sleep(1)
        return self.xtcp.code  # 返回分享码

    def startXTCPVisitor(self, serverAddr, token, uid, sk, localPort, localIP='127.0.0.1'):
        self.mode = "XTCP"
        self.xtcp = XTCP(serverAddr=serverAddr, token=token)
        thread.start_new_thread(self.xtcp.startVisitor, (uid, sk, localPort, localIP))

    def joinAisleCode(self, serverAddr, token, AisleCode, localPort):
        mode, uid, sk = Aisle.phaseAisleCode(AisleCode=AisleCode)
        if mode == 'XTCP':
            self.mode = mode
            self.startXTCPVisitor(serverAddr=serverAddr, token=token, uid=uid, sk=sk, localPort=localPort)

    @classmethod
    def generateXTCPCode(cls, mode: str, uid: str, sk: str):
        load = uid + sk
        load = load.encode('utf-8')
        load = b64encode(load)
        load = str(load, 'utf-8')
        logging.debug(load)
        XTCPCode = f'{mode}://{load}'
        return XTCPCode

    @classmethod
    def phaseAisleCode(cls, AisleCode: str):
        mode, load = AisleCode.split('://')
        if mode == 'XTCP':
            load = str(b64decode(load), 'utf-8')
            uid = load[:UID_LENGTH]
            sk = load[UID_LENGTH:]
            return mode, uid, sk
        else:
            return mode, 0, 0


class FrpCtl(AisleDefault):  # 用来创建、控制单个frp进程的类
    def __init__(self):
        super(FrpCtl, self).__init__()
        self.logger.info('初始化Frp模块...')
        self.logger.info('初始化参数...')
        # 确定frp相对路径，仅支持windows和linux识别
        self.hostname = gethostname()
        self.system = platform.system().lower()
        arch = platform.architecture()[0][0:2]
        self.binDir = f'./bin/' \
                      f'frp_' \
                      f'{FRP_VERSION}_' \
                      f'{self.system}_' \
                      f'amd{arch}'  # 直接写入amd作为临时解决方案
        if os.path.exists(self.binDir):
            pass
        else:
            self.logger.warning(f'没有找到对应的frp文件，frp将无法启动，请联系开发者以获取帮助。检测到的操作系统:{self.system} {arch}')

        # 初始化一个字符串作为工作模式
        self.mode = ''

        # 初始化一个字典作为额外的启动参数
        self.startArgs = {}
        self.frp = None


class FrpClient(FrpCtl):  # 所有Client和一个Server通信
    def __init__(self, serverAddr, token):

        super(FrpClient, self).__init__()

        self.binPath = self.binDir + '/frpc'
        if self.system == 'windows':
            self.logger.debug('对windows系统下的执行路径进行替换')
            self.binPath = self.binPath.replace('/', '\\')
            self.binPath += '.exe'

        self.logger.debug(f'使用二进制文件{self.binPath}')
        if os.path.exists(self.binDir):
            pass
        else:
            self.logger.warning(f'没有找到对应的frpc软件，frp将无法启动，请联系开发者以获取帮助。'
                                f'使用二进制文件{self.binPath}')

        self.startArgs = {
            **self.startArgs,
            '--server_addr': serverAddr,
            '--token': token
        }

        self.logger.info('初始化frp完成')

    def __del__(self):
        self.logger.info('关闭frp进程')
        if self.frp:
            self.frp.terminate()

    def startSubprocess(self):
        subprocessArgs = [self.binPath, self.mode]
        for args, val in self.startArgs.items():
            subprocessArgs.append(f'{args}')
            subprocessArgs.append(f'{val}')
        self.logger.debug(f'subprocess:{subprocessArgs}')

        magicString = ''  # DEBUG用，shell代码
        for i in subprocessArgs:
            magicString = magicString + i + ' '
        self.logger.debug(f'将执行:{magicString}')

        self.logger.info('启动frpc外部进程')
        self.frp = Popen(
            args=subprocessArgs,
            stdout=PIPE,
            shell=True,
            stderr=STDOUT
        )
        with self.frp.stdout:
            logSubprocessOutput(self.frp.stdout, self.logger)


class XTCP(FrpClient):
    def __init__(self, serverAddr, token):
        super(XTCP, self).__init__(serverAddr, token)
        self.mode = 'xtcp'
        self.uid = 'test'
        self.code = ''

    def startHost(self, sk, localPort, localIP='127.0.0.1'):
        self.logger.info(f'将使用XTCP作为主机')

        self.uid = shortuuid.ShortUUID(alphabet="0123456789ABCDEF").random(UID_LENGTH)
        self.logger.debug(self.uid)
        self.startArgs = {
            **self.startArgs,
            '--role': 'server',
            '--local_ip': localIP,
            '--local_port': localPort,
            '--proxy_name': self.uid,
            '--sk': sk
        }

        self.logger.debug(f'使用{self.uid}作为uid')

        self.code = Aisle.generateXTCPCode(mode='XTCP', uid=self.uid, sk=sk)
        self.startSubprocess()

    def startVisitor(self, uid, sk, localPort, localIP='127.0.0.1'):
        self.logger.info(f'使用XTCP作为访客')
        self.startArgs = {
            **self.startArgs,
            '--role': 'visitor',
            '--bind_addr': localIP,
            '--bind_port': localPort,
            '--proxy_name': uid,
            '--sk': sk
        }
        self.startSubprocess()
