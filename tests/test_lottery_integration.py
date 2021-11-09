from brownie import network
import pytest
from scripts.helpfull_scripts import (
    LOCALE_BLOCKCHAIN_ENVIRONTMENTS,
    get_account,
    fund_with_link,
)
from scripts.deploy_lottery import deploy_lottery
import time


def test_can_pick_winner():
    if network.show_active() in LOCALE_BLOCKCHAIN_ENVIRONTMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.start_lottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntrance()})
    lottery.enter({"from": account, "value": lottery.getEntrance()})
    fund_with_link(lottery)
    lottery.end_lottery({"from": account})
    time.sleep(120)
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
