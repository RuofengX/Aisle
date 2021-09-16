# Aisle的核心
import socket

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
    format='%(asctime)s [%(levelname)s] %(name)s(%(funcName)s):\t%(message)s'
)


def decodeB64String(raw: str):
    """
    :param raw: 源被编码的字符串
    :return:  解码后的字符串
    """
    return str(b64decode(raw), 'utf-8')


def encodeB64String(raw: str):
    """
    :param raw: 原正常字符串
    :return:  编码后的字符串
    """
    return str(b64encode(raw.encode('utf-8')), 'utf-8')


# 使用logging记录subprocess的输出，来自 https://stackoverflow.com/questions/21953835/run-subprocess-and-print-output-to-logging
def logSubprocessOutput(pipe, logger):
    codec = chardet.detect(pipe.readline(100))['encoding']  # 获取编码方式
    logging.debug(f'PIPE开头：{pipe.readline()}')
    for line in iter(pipe.readline, b''):
        line = line.decode(codec).replace('\n', '')  # 删去行末的/n，logging自动会换行
        logger.info(line)


# 自带logger配置
class AisleDefault(object):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(LOG_LEVEL)
        self.logger.debug('日志功能启动')


class Aisle(AisleDefault):  # 核心控制类，对应vps/用户电脑
    def __init__(self):
        super().__init__()
        self.logger.info('初始化Aisle...')
        self.NATType = ''
        self.localIP = socket.gethostbyname(socket.gethostname())
        self.clientModule = {}  # 存储各个模块的实例的字典  # TODO:
        self.clientHandler = {}  # 存储各个模块的线程实例的字典  # TODO:

        self.logger.info('初始化完成')

    def __del__(self):
        for handler in self.clientModule.values():
            del handler

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

    def __phaseAisleCode(self, code: str):
        """
        将AisleCode联机码转换为各个参数
        :param code: AisleCode
        :return: 参数均为字符串,所有B64编码在此已解码
        """
        mode, _rest = code.split('://', maxsplit=1)
        serverInfo, _rest = _rest.split('/', 1)
        token, _rest = _rest.split('/', 1)
        if '/' in _rest:
            payload = _rest.split('/')[0]
            self.logger.error(f'超出预期的联机码，联机码可能有错误 {code} ，超出预期的部分：/{_rest}')
        else:
            payload = _rest

        # 处理serverInfo部分
        serverInfoStr = decodeB64String(serverInfo)
        serverIP, port = serverInfoStr.split(':')

        # 处理token部分
        token = decodeB64String(token)

        # 处理payload部分
        payload = decodeB64String(payload)

        return mode, serverIP, port, token, payload

    def joinAisleCode(self, code, localPort):
        """

        :param code: 联机码，形如： ProtocolName://(B64_ServerInfo)/(B64_ServerToken)/(B64_Payload)
        :param localPort:  指定Aisle所绑定的远程服务到本地的端口
        :return: 直接尝试加入服务器，无返回值
        """

        mode, serverIP, port, token, payload = self.__phaseAisleCode(code)
        if mode == 'XTCP':
            self.xtcp = XTCP(serverIP=serverIP, serverPort=port, token=token)
            thread.start_new_thread(self.xtcp.startVisitor, (payload, localPort, self.localIP))
        elif mode == 'STCP':
            self.stcp = STCP(serverIP=serverIP, serverPort=port, token=token)
            thread.start_new_thread(self.stcp.startVisitor, (payload, localPort, self.localIP))

    def startXTCPHost(self, serverIP, serverPort, token, sk, localPort):
        _mode = 'stcp'
        self.clientModule[_mode] = XTCP(serverIP=serverIP, serverPort=serverPort, token=token)
        self.clientHandler[_mode] = thread.start_new_thread(self.clientModule['xtcp'].startHost, (sk, localPort))  # 实用新线程启动外部程序  # TODO:需要改进
        # TODO:实例线程阻塞时删除实例导致__del__无法被触发，考虑添加结束函数手动处理
        sleep(1)
        return self.xtcp.generateAisleCode()  # 返回联机码的Payload

    def startSTCPHost(self, serverIP, serverPort, token, sk, localPort):
        self.clientModule['stcp'] = STCP(serverIP=serverIP, serverPort=serverPort, token=token)
        thread.start_new_thread(self.clientModule['stcp'].startHost, (sk, localPort))  # 实用新线程启动外部程序  # TODO:需要改进
        # TODO:实例线程阻塞时删除实例导致__del__无法被触发，考虑添加结束函数手动处理，同样这里也是
        sleep(1)
        return self.stcp.generateAisleCode()  # 返回联机码的Payload


class AisleClientModuleMixin(AisleDefault):
    def __init__(self, serverIP, serverPort, token):
        AisleDefault.__init__(self)
        self.mode = ''
        self.serverIP = serverIP
        self.serverPort = serverPort
        self.token = token
        self.payload = ''

    def generateAisleCode(self):
        """
        所有的Client模块都要有生成AisleCode的功能，都要有self.payload
        :return: AisleCode联机码
        """
        code = f'{self.mode}://'

        ServerInfo = encodeB64String(f'{self.serverIP}:{self.serverPort}')
        code += ServerInfo

        code += '/'

        Token = encodeB64String(self.token)
        code += Token

        code += '/'

        if self.payload == '':
            self.logger.warning('模块提供了一个空的payload')
        Payload = encodeB64String(self.payload)
        code += Payload

        return code


class FrpCtl(AisleDefault):  # 用来创建、控制单个frp进程的类，
    def __init__(self):
        AisleDefault.__init__(self)

        self.logger.info('初始化frp模块...')

        # 确定frp相对路径，仅支持windows和linux识别
        self.hostname = gethostname()

        # 处理操作系统名称
        self.system = platform.system().lower()

        # 处理架构
        _arch = platform.architecture()[0][0:2]
        if _arch == '64':
            pass
        elif _arch == '32':
            _arch = ''

        self.binDir = f'./bin/' \
                      f'frp_' \
                      f'{FRP_VERSION}_' \
                      f'{self.system}_' \
                      f'amd{_arch}'  # 直接写入amd作为临时解决方案
        if os.path.exists(self.binDir):
            pass
        else:
            self.logger.warning(f'没有找到对应的frp文件，frp将无法启动，请联系开发者以获取帮助。检测到的操作系统:{self.system} {_arch}')

        # 初始化一个字符串作为工作模式
        self.mode = ''

        # 抛弃！初始化一个字典作为额外的启动参数
        # self.startArgs = {}

        # 配置文件路径
        self.configFilePath = ''

        # 使用config字典存储配置
        self.config = {
            'common': {},  # 存储common
            'proxy': {}  # 存储多个proxy
        }
        # 用以存储Popen的实例
        self.handler = None

    def __del__(self):
        if os.path.exists(self.configFilePath):
            if LOG_LEVEL == 'DEBUG':
                with open(self.configFilePath, mode='r', encoding='utf-8') as f:
                    self.logger.debug('-------临时配置文件内容开始-------')
                    for line in f.readlines():
                        line = line.split('\n')[0]
                        self.logger.debug(line)
                    self.logger.debug('-------临时配置文件内容结束-------')

                self.logger.warning(f'删除临时配置文件')
                os.remove(self.configFilePath)

    @staticmethod
    def _item2Config(item):
        """
        将字典的item变为frp.ini中的一行字符串
        :param item: 字典的一个item
        :return: 一行字符串
        """
        name, val = item
        return f'{name} = {val}'

    def writeConf(self):
        if not os.path.exists(TEMP_DIR):
            os.mkdir(TEMP_DIR)
        self.configFilePath = f'{TEMP_DIR}/frpc.ini'
        self.logger.debug(f'配置文件路径：{self.configFilePath}')

        with open(self.configFilePath, mode='w', encoding='utf-8') as f:

            # 写入common部分
            f.write('[common]\n')
            for item in self.config['common'].items():  # 遍历字典写入所有参数
                f.write(self._item2Config(item) + '\n')

            # 写入各个proxy部分
            for proxyName, proxyConfig in self.config['proxy'].items():
                f.write(f'[{proxyName}]\n')
                for item in proxyConfig.items():
                    f.write(self._item2Config(item) + '\n')


class FrpClient(AisleClientModuleMixin, FrpCtl):  # 所有Client和一个Server通信
    def __init__(self, serverIP, serverPort, token):
        # 多继承要一个个轮流初始化，super()只会横向搜索同深度的第一个构造函数
        FrpCtl.__init__(self)
        AisleClientModuleMixin.__init__(self, serverIP=serverIP, serverPort=serverPort, token=token)  # 这里尤其注意加self

        self.binPath = self.binDir + '/frpc'
        if self.system == 'windows':
            self.logger.debug('对windows系统下的执行路径进行替换')
            self.binPath = self.binPath.replace('/', '\\')
            self.binPath += '.exe'

        self.logger.debug(f'使用二进制文件{self.binPath}')
        if os.path.exists(self.binPath):
            pass
        else:
            self.logger.error(f'没有找到对应的frpc软件，frp将无法启动，请联系开发者以获取帮助。'
                              f'使用二进制文件{self.binPath}')
        '''
        # 抛弃命令行模式
        self.startArgs = {
            **self.startArgs,
            '--server_addr': serverIP + ':' + serverPort,
            '--token': token
        }
        '''
        # 使用config字典存储
        self.config['common']['server_addr'] = serverIP
        self.config['common']['server_port'] = serverPort
        self.config['common']['token'] = token

        self.logger.info('初始化frp完成')

    def __del__(self):
        self.logger.debug('析构函数开始运行')
        FrpCtl.__del__(self)  # 继承FrpCtl的析构函数
        if self.handler:
            self.handler.terminate()
            self.logger.debug('结束外部进程')

    def startSubprocess(self):
        if self.handler is None:
            pass
        else:
            self.logger.error('存在已经实例化的外部进程，请不要用同一个frp实例创建多个外部进程！')
            return -1

        self.logger.info('启动frpc外部进程')
        self.writeConf()  # 将配置写入文档
        _args = [self.binPath, '-c', self.configFilePath]
        self.logger.debug(f'_args: {_args}')

        if LOG_LEVEL == 'DEBUG':
            _magicString = ''
            for i in _args:
                _magicString += f'{i} '
            self.logger.debug(f'魔法代码：{_magicString}')

        self.handler = Popen(
            args=_args,
            stdout=PIPE,
            shell=True,
            stderr=STDOUT
        )
        with self.handler.stdout:
            logSubprocessOutput(self.handler.stdout, self.logger)
        self.logger.critical('frp外部进程结束')


class XTCP(FrpClient):
    def __init__(self, serverIP, serverPort, token):
        super(XTCP, self).__init__(serverIP, serverPort, token)

        self.uid = ''
        self.mode = 'XTCP'

    @classmethod
    def generatePayload(cls, uid: str, sk: str):
        payload = uid + sk
        return payload

    @classmethod
    def phasePayload(cls, payload):
        uid = payload[:UID_LENGTH]
        sk = payload[UID_LENGTH:]
        return uid, sk

    def startHost(self, sk, localPort, localIP='127.0.0.1'):
        """
        :param self:
        :param sk: 可选自定义密码
        :param localPort: 绑定的本地链接
        :param localIP: 本机IP， 后备选项为127.0.0.1
        :return: 无返回值即代表正常运行，返回0代表外部进程结束，但是要保证实例在启动之后，self.payload为有效的分享码的payload
        """

        self.logger.info(f'将使用XTCP作为主机')

        self.uid = shortuuid.ShortUUID(alphabet="0123456789ABCDEF").random(UID_LENGTH)

        '''
        # 抛弃
        self.startArgs = {
            **self.startArgs,
            '--role': 'server',
            '--local_ip': localIP,
            '--local_port': localPort,
            '--proxy_name': self.uid
        }
        '''
        self.config['proxy'][self.uid] = {
            'type': self.mode.lower(),  # 配置文件中小写mode
            'role': 'server',
            'local_ip': localIP,
            'local_port': localPort
        }

        # 兼容空字符串的sk
        if sk == '':
            pass
        else:
            '''
            # 抛弃
            self.startArgs = {
                **self.startArgs,
                '--sk': sk
            }
            '''
            self.config['proxy'][self.uid]['sk'] = sk

        # self.logger.debug(f'启动参数 {self.startArgs}')
        self.logger.debug(f'启动参数 {self.config}')

        # 启动前生成XTCPCode
        self.payload = self.generatePayload(uid=self.uid, sk=sk)

        # 启动外部进程
        self.startSubprocess()

    def startVisitor(self, payload, _localPort, _localIP='127.0.0.1'):
        self.logger.info(f'使用XTCP作为访客')
        _uid, _sk = self.phasePayload(payload=payload)
        '''
        # 抛弃
        self.startArgs = {
            **self.startArgs,
            '--role': 'visitor',
            '--bind_addr': localIP,
            '--bind_port': localPort,
            '--proxy_name': uid,
            '--sk': sk
        }
        '''
        self.config['proxy'][f'{_uid}-visitor'] = {
            'type': self.mode.lower(),
            'role': 'visitor',
            'server_name': _uid,
            'bind_address': _localIP,
            'bind_port': _localPort
        }

        if _sk == '':
            pass
        else:
            self.config['proxy'][f'{_uid}-visitor']['sk'] = _sk

        self.startSubprocess()


class STCP(FrpClient):
    def __init__(self, serverIP, serverPort, token):
        super(STCP, self).__init__(serverIP, serverPort, token)

        self.uid = ''
        self.mode = 'STCP'

    @classmethod
    def generatePayload(cls, uid: str, sk: str):
        payload = uid + sk
        logging.debug(payload)
        return payload

    @classmethod
    def phasePayload(cls, payload):
        uid = payload[:UID_LENGTH]
        sk = payload[UID_LENGTH:]
        return uid, sk

    def startHost(self, sk, localPort, localIP='127.0.0.1'):
        """
        :param self:
        :param sk: 可选自定义密码
        :param localPort: 绑定的本地链接
        :param localIP: 本机IP， 后备选项为127.0.0.1
        :return: 无返回值即代表正常运行，返回0代表外部进程结束，但是要保证实例在启动之后，self.payload为有效的分享码的payload
        """

        self.logger.info(f'将使用STCP作为主机')

        self.uid = shortuuid.ShortUUID(alphabet="0123456789ABCDEF").random(UID_LENGTH)

        self.config['proxy'][self.uid] = {
            'type': self.mode.lower(),  # 配置文件中小写mode
            'role': 'server',
            'local_ip': localIP,
            'local_port': localPort
        }

        # 兼容空字符串的sk
        if sk == '':
            pass
        else:
            self.config['proxy'][self.uid]['sk'] = sk

        # self.logger.debug(f'启动参数 {self.startArgs}')
        self.logger.debug(f'启动参数 {self.config}')

        # 启动前生成XTCPCode
        self.payload = self.generatePayload(uid=self.uid, sk=sk)

        # 启动外部进程
        self.startSubprocess()

    def startVisitor(self, payload, _localPort, _localIP='127.0.0.1'):
        self.logger.info(f'使用STCP作为访客')
        _uid, _sk = self.phasePayload(payload=payload)
        self.config['proxy'][f'{_uid}-visitor'] = {
            'type': self.mode.lower(),
            'role': 'visitor',
            'server_name': _uid,
            'bind_address': _localIP,
            'bind_port': _localPort
        }

        if _sk == '':
            pass
        else:
            self.config['proxy'][f'{_uid}-visitor']['sk'] = _sk

        self.startSubprocess()


if __name__ == '__main__':
    core = Aisle()
    # code = core.startXTCPHost(serverIP=SERVER_DOMAIN, serverPort=SERVER_PORT, token='ONLY_FOR_TEST', localPort='25565', sk='0')
    core.joinAisleCode(code='STCP://Z2F0ZS5vYXItMC5zaXRlOjgwODA=/T05MWV9GT1JfVEVTVA==/QTNENjIw', localPort='25565')
    while 1:
        pass
