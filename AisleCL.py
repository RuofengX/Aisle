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


@AisleCL.command(help='启动xtcp主机')
def xtcpHost():
    pass  # TODO: 添加自动启动xtcp的CL入口


@AisleCL.command(help='启动xtcp主机')
def xtcpVisitors():
    pass  # TODO: 添加自动启动xtcp的CL入口


if __name__ == '__main__':
    AisleCL()
