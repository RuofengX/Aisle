#  Aisle的命令行程序，默认和OAR的服务器通信
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
@click.option('--server_ip', default=SERVER_IP)
@click.option('--server_port', default=SERVER_PORT)
@click.option('--token', default=SERVER_TOKEN)
@click.option('--local_port', default='25565')
@click.option('--secret_key', default='')
def start_xtcp(server_ip, server_port, token, local_port, secret_key):
    core0 = Aisle.Aisle()
    AisleCode = core0.startXTCPHost(serverIP=server_ip, serverPort=server_port, token=token, sk=secret_key,
                                    localPort=local_port, tls=True)
    click.echo(f'本次联机码为： {AisleCode}')
    click.echo('联机码是访问您电脑的唯一凭证，请妥善保管')
    while 1:
        pass


@AisleCL.command(help='使用STCP作为主机')
@click.option('--server_ip', default=SERVER_DOMAIN)
@click.option('--server_port', default=SERVER_PORT)
@click.option('--token', default=SERVER_TOKEN)
@click.option('--local_port', default='25565')
@click.option('--secret_key', default='')
def start_stcp(server_ip, server_port, token, local_port, secret_key):
    core0 = Aisle.Aisle()
    AisleCode = core0.startSTCPHost(serverIP=server_ip, serverPort=server_port, token=token, sk=secret_key,
                                    localPort=local_port, tls=True)
    click.echo(f'本次联机码为： {AisleCode}')
    click.echo('联机码是访问您电脑的唯一凭证，请妥善保管')
    while 1:
        pass
    # TODO 添加鉴权机制，适当对流量转发收费


@AisleCL.command(help='使用分享码加入别的主机')
@click.option('--localPort', default='25565')
@click.option('--token', default=SERVER_TOKEN)
@click.argument('AisleCode')
def join(localport, aislecode, token):
    core0 = Aisle.Aisle()
    core0.joinAisleCode(_code=aislecode, localPort=localport, _token=token, tls=True)
    while 1:
        pass


if __name__ == '__main__':
    AisleCL()
