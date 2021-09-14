import click
from config import *
import NATTypeDetector as natTest


@click.group()
def Aisle():
    pass


@Aisle.command(help='查看软件信息')
def info():
    click.echo(f'This is OAR Aisle {VERSION}')
    click.echo(f'{INFO_EN}')
    click.echo(f'这里是 OAR Aisle {VERSION}')
    click.echo(f'{INFO_ZH}')


@Aisle.command(help='我的回合，抽卡！ --对家宽质量做出评价，结果决定了能否能够联机')
def test():
    click.echo(f'{NAT_TEST_START}')
    click.echo(f'{NAT_HELP}')
    natType = natTest.test()[0]
    if natType in NAT_TYPE_MAP.keys():
        natQuality = NAT_TYPE_MAP[natType]
    else:
        natQuality = f"???_{natType}"
    click.echo(f'{NAT_TYPE_IS} ' + natQuality)


# 测试
@click.command()
def choice():
    test()


if __name__ == '__main__':
    print('这是一个命令行程序，您应该从命令行启动它')
    Aisle()
    choice()
