from ape import project
from ape.cli import get_user_selected_account


def main():
    account = get_user_selected_account()
    account.deploy(project.WETH8)
