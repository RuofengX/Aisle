#  Aisle的命令行程序
import Aisle
import click
from config import *

core = Aisle.Aisle()


@click.group()
def AisleCL():
    pass


@AisleCL.command(help='查看软件信息')
def info():
    click.echo(f'这里是 OAR Aisle {VERSION}')
    click.echo(f'{INFO}')


@AisleCL.command(help='我的回合，抽卡！ --对家宽质量做出评价，结果决定了能否能够联机')
def test():
    click.echo(f'{NAT_TEST_START}')
    click.echo(f'{NAT_HELP}')
    click.echo(f'{NAT_TYPE_IS} ' + core.getNATType(ifCute=True))


@AisleCL.command(help='使用XTCP作为主机')
@click.option('--server', default='gate.oar-0.site:8080')
@click.option('--token', default='ONLY_FOR_TEST')
@click.option('--localPort', default='25565')
@click.argument('password')
def xtcpHost(server, token, localport, password):
    core0 = Aisle.Aisle()
    AisleCode = core0.startXTCPHost(serverAddr=server, token=token, sk=password, localPort=localport)
    click.echo(f'本次联机码为： {AisleCode}')
    click.echo('联机码是访问您电脑的唯一凭证，请妥善保管')
    while 1:
        pass


@AisleCL.command(help='使用分享码加入别的主机')
@click.option('--server', default='gate.oar-0.site:8080')
@click.option('--token', default='ONLY_FOR_TEST')
@click.option('--localPort', default='25565')
@click.argument('AisleCode')
def join(server, token, localport, aislecode):
    core0 = Aisle.Aisle()
    core0.joinAisleCode(serverAddr=server, token=token, AisleCode=aislecode, localPort=localport)
    while 1:
        pass


if __name__ == '__main__':
    AisleCL()
