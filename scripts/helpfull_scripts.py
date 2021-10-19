from brownie import network, config, accounts, Contract

from scripts.deploy_lottery import deploy_lottery

FORKED_LOCALE_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
LOCALE_BLOCKCHAIN_ENVIRONTMENTS = ["development", "ganache-locale"]


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCALE_BLOCKCHAIN_ENVIRONTMENTS
        or network.show_active() in FORKED_LOCALE_ENVIRONMENTS
    ):
        return accounts[0]

    return accounts.add(config["wallet"]["from_key"])


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
}


def get_contract(contract_name):
    """
    This function will grab the contract addresses from the brownie config if definied,
    otherwise, it will deploy amoch version of that contract and return that mock contract.

        Args:
            contract_name = string

        Returns:
            brownie.network.contract.ProjectContract: The most recently deployed version of this contract.
    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCALE_BLOCKCHAIN_ENVIRONTMENTS:
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        # Address
        # Abi
        contract = Contract.from_abi(
            contract_type._name,
            contract_address,
            contract_type.abi
            # MockV3Aggregator has .abi (creating contract from his abi code) methode and ._name for the name
        )
    return contract


DECIMALS = 8
INITIAL_VALUE = 200000000000


def deploy_mocks(decimals=DECIMALS, initial_value=INITIAL_VALUE):
    account = get_account()
    mock_price_feed = MockV3Aggregator.deploy(
        decimals, initial_value, {"from": account}
    )
