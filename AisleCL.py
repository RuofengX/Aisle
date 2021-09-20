#  Aisle的命令行程序，默认和OAR的服务器通信
import Aisle
import click
from config import *


class AisleHandler(AisleDefault):  # 一个core的操作句柄
    def __init__(self):
        super(AisleHandler, self).__init__()
        self.core = None
        self.code = ''

    def create(self):
        if self.core is None:
            self.core = Aisle.Aisle()

        else:
            self.logger.warning(f'存在Aisle.Aisle实例，将不再创建:\t {self.core}')
        return self.core

    def hold(self):
        if self.core is None:
            LOG.warning(f'core实例为None')
            return
        LOG.debug(f'挂起CL进程')
        self.__loop()

    def __loop(self):
        try:
            LOG.debug('CL主进程挂起')
            while 1:
                pass
        except Exception as _:
            LOG.critical(f'[致命错误]{_}结束挂起')
            self.__core_terminal()

    def __core_terminal(self):
        if self.core is None:
            self.logger.debug(f'销毁实例\t {self.core}')
            del self.core
        else:
            self.logger.warning(f'不存在Aisle.Aisle实例，不操作{self.core}')

    def startXTCPHost(self, server_ip, server_port, token, secret_key, local_port='25565', tls=True):
        self.create()
        self.code = self.core.startXTCPHost(serverIP=server_ip, serverPort=server_port, token=token, sk=secret_key,
                                            localPort=local_port, tls=tls)

    def startSTCPHost(self, server_ip, server_port, token, secret_key, local_port='25565', tls=True):
        self.create()
        self.code = self.core.startSTCPHost(serverIP=server_ip, serverPort=server_port, token=token, sk=secret_key,
                                            localPort=local_port, tls=tls)

    def join(self, _code, token, local_port='25565', tls=True):
        self.create()
        self.code = self.core.joinAisleCode(_code=_code, _token=token, localPort=local_port, tls=tls)

    @property
    def NAT(self):
        self.create()
        self.core.getNATType(ifCute=True)
        return self.core.getNATType(ifCute=True)


@click.group()
def AisleCL():
    pass


@AisleCL.command(help='查看软件信息')
def info():
    click.echo(f'这里是 OAR Aisle CL {VERSION}')
    click.echo(f'{INFO}')


@AisleCL.command(help='我的回合，抽卡！ --对家宽质量做出评价，结果决定了能否能够联机')
def test():
    hd = AisleHandler()
    click.echo(f'{NAT_TEST_START}')
    click.echo(f'{NAT_HELP}')
    click.echo(f'{NAT_TYPE_IS} ' + hd.NAT)


@AisleCL.command(help='使用XTCP作为主机')
@click.option('--server_ip', default=SERVER_IP)
@click.option('--server_port', default=SERVER_PORT)
@click.option('--token', default=SERVER_TOKEN)
@click.option('--local_port', default='25565')
@click.option('--secret_key', default='')
def start_xtcp(server_ip, server_port, token, local_port, secret_key):
    hd = AisleHandler()
    hd.startXTCPHost(server_ip=server_ip, server_port=server_port, token=token, secret_key=secret_key,
                     local_port=local_port)
    click.echo(SPLIT_LINE)
    click.echo(f'本次联机码为： {hd.code}')
    click.echo('联机码是访问您电脑的唯一凭证，请妥善保管')
    click.echo(SPLIT_LINE)

    LOG.debug(f'开始阻塞')
    hd.hold()


@AisleCL.command(help='使用STCP作为主机')
@click.option('--server_ip', default=SERVER_DOMAIN)
@click.option('--server_port', default=SERVER_PORT)
@click.option('--token', default=SERVER_TOKEN)
@click.option('--local_port', default='25565')
@click.option('--secret_key', default='')
def start_stcp(server_ip, server_port, token, local_port, secret_key):
    hd = AisleHandler()
    hd.startSTCPHost(server_ip=server_ip, server_port=server_port, token=token, secret_key=secret_key,
                     local_port=local_port)
    click.echo(SPLIT_LINE)
    click.echo(f'本次联机码为： {hd.code}')
    click.echo('联机码是访问您电脑的唯一凭证，请妥善保管')
    click.echo(SPLIT_LINE)

    LOG.debug(f'开始阻塞')
    hd.hold()
    # TODO 添加鉴权机制，适当对流量转发收费


@AisleCL.command(help='使用分享码加入别的主机')
@click.option('--localPort', default='25565')
@click.option('--token', default=SERVER_TOKEN)
@click.option('--aislecode', default='')
def join(localport, aislecode, token):
    if aislecode == '':
        aislecode = input('请在这里输入或粘贴联机码，回车键结束\n')
        aislecode.strip()  # 必须删除两端空格
    hd = AisleHandler()
    try:
        hd.join(_code=aislecode, token=token, local_port=localport)
        LOG.debug(f'开始阻塞')
        hd.hold()
    except Exception as exp:
        LOG.critical(f'发生{exp}错误')
    click.echo('进程结束')


if __name__ == '__main__':
    LOG.critical(SPLIT_LINE)
    LOG.critical(f'您正在使用一个未经充分测试的预发布版本')
    LOG.critical(f'发现任何Bug请与作者weiruofeng@outlook.com联系')
    LOG.critical(SPLIT_LINE)
    AisleCL()
