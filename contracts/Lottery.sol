// SPDX-License-Identifier: MIT

pragma solidity ^0.6.6;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";

contract Lottery {
    address[] public players;
    uint256 usdEntryFee;
    AggregatorV3Interface internal ethPriceFeed;

    enum LOTERY_STATE{
        OPEN,
        CLOSED,
        CALCULATING_WINNER,
    }

    constructor(address _priceFeedAddress) public {
        usdEntryFee = 50 * (10**18);
        ethPriceFeed = AggregatorV3Interface(_priceFeedAddress);
    }

    function enter() public payable {
        require(msg.value >= getEntrance(), "NOT enough ETH");
        players.push(msg.sender);
    }

    function getEntrance() public view returns (uint256) {
        (, int256 price, , , ) = ethPriceFeed.latestRoundData();
        uint256 adjustedPrice = uint256(price) * (10**10);
        uint256 costToEnter = (usdEntryFee * 10**18) / adjustedPrice;
        return costToEnter;
    }
}
