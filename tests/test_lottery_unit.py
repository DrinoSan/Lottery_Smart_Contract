# ETH 3.760 Dollar
# 0.01329 ~ 50 Dollar
# 13000000000000000
from brownie import accounts, Lottery, config, network, exceptions
from eth_utils import address
import pytest
from scripts.deploy_lottery import deploy_lottery
from web3 import Web3

from scripts.helpfull_scripts import (
    LOCALE_BLOCKCHAIN_ENVIRONTMENTS,
    get_account,
    fund_with_link,
    get_contract,
)


# TODO:
# Refactor to make it work for mocks and testnet and so on
def test_get_entrance_fee():
    if network.show_active() not in LOCALE_BLOCKCHAIN_ENVIRONTMENTS:
        pytest.skip
    # Arrange
    lottery = deploy_lottery()
    # Act
    expected_entrance_fee = Web3.toWei(0.025, "ether")
    entrance_fee = lottery.getEntrance()
    # Assert
    print(f"Entrance fee: {entrance_fee}")
    assert expected_entrance_fee == entrance_fee


def test_cant_enter_unless_started():
    # Arrange
    if network.show_active() not in LOCALE_BLOCKCHAIN_ENVIRONTMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    # Act / Assert
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": get_account(), "value": lottery.getEntrance()})


def test_can_start_and_enter_lottery():
    # Arrange
    if network.show_active() not in LOCALE_BLOCKCHAIN_ENVIRONTMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    # Act
    lottery.start_lottery()
    lottery.enter({"from": account, "value": lottery.getEntrance()})
    # Assert
    assert lottery.players(0) == account


def test_can_end_lottery():
    # Arrange
    if network.show_active() not in LOCALE_BLOCKCHAIN_ENVIRONTMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.start_lottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntrance()})
    fund_with_link(lottery)
    lottery.endLottery({"from": account})
    assert lottery.lottery_state() == 2


def test_can_pick_winner2():
    # Arrange
    if network.show_active() not in LOCALE_BLOCKCHAIN_ENVIRONTMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.start_lottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntrance()})
    lottery.enter({"from": get_account(index=1), "value": lottery.getEntrance()})
    lottery.enter({"from": get_account(index=2), "value": lottery.getEntrance()})
    fund_with_link(lottery)
    transaction = lottery.endLottery({"from": account})
    requestId = transaction.events["RequestedRandomness"]["requestId"]
    STATIC_RNG = 777
    get_contract("vrf_coordinator").callBackWithRandomness(
        requestId, STATIC_RNG, lottery.address, {"from": account}
    )

    starting_balance_of_account = account.balance()
    starting_balance_of_lottery = lottery.balance()

    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
    assert (
        account.balance() == starting_balance_of_account + starting_balance_of_lottery
    )
