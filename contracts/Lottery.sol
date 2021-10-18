// SPDX-License-Identifier: MIT

pragma solidity ^0.6.6;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract Lottery is Ownable {
    address[] public players;
    uint256 usdEntryFee;
    AggregatorV3Interface internal ethPriceFeed;

    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }

    LOTTERY_STATE public lottery_state;

    constructor(address _priceFeedAddress) public {
        usdEntryFee = 50 * (10**18);
        ethPriceFeed = AggregatorV3Interface(_priceFeedAddress);
        lottery_state = LOTTERY_STATE.CLOSED;
    }

    function enter() public payable {
        require(
            lottery_state == LOTTERY_STATE.OPEN,
            "Lottery is currently closed"
        );
        require(msg.value >= getEntrance(), "NOT enough ETH");
        players.push(msg.sender);
    }

    function getEntrance() public view returns (uint256) {
        (, int256 price, , , ) = ethPriceFeed.latestRoundData();
        uint256 adjustedPrice = uint256(price) * (10**10);
        uint256 costToEnter = (usdEntryFee * 10**18) / adjustedPrice;
        return costToEnter;
    }

    function start_lottery() public onlyOwner {
        require(lottery_state == LOTTERY_STATE.CLOSED, "Can't start lottery");
        lottery_state = LOTTERY_STATE.OPEN;
    }

    function end_lottery() public onlyOwner {
        // Pseude random number -> do not put in production friendly reminder :D
        uint256(
            keccak256(
                abi.encodePacked(
                    nonce, // is predicatble ( number of transactions )
                    msg.sender, // is predicatble
                    block.difficulty, // can be manipulated by the miners
                    block.timestamp // is predicatble
                )
            )
        ) % players.length;
    }
}
