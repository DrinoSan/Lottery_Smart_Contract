# ETH 3.760 Dollar
# 0.01329 ~ 50 Dollar
# 13000000000000000

from brownie import accounts, Lottery, config, network
from web3 import Web3


# TODO:
# Refactor to make it work for mocks and testnet and so on
def test_get_entrance_fee():
    account = accounts[0]
    lottery = Lottery.deploy(
        config["networks"][network.show_active()].get("eth_usd_price_feed"),
        {"from": account},
    )
    print(f"FEE is: {lottery.getEntrance()}")
    assert lottery.getEntrance() > Web3.toWei(0.012, "ether")
    assert lottery.getEntrance() < Web3.toWei(0.015, "ether")
