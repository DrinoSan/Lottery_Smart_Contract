// SPDX-License-Identifier: MIT

pragma solidity ^0.6.6;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol";

contract Lottery is VRFConsumerBase, Ownable {
    address payable[] public players;
    uint256 public usdEntryFee;
    address payable public recentWinner;
    uint256 public randomness;
    AggregatorV3Interface internal ethPriceFeed;

    uint256 public fee;
    bytes32 public keyhash;

    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }

    LOTTERY_STATE public lottery_state;

    constructor(
        address _priceFeedAddress,
        address _vrf_coordinator,
        address _link,
        uint256 _fee,
        bytes32 _keyhash
    ) public VRFConsumerBase(_vrf_coordinator, _link) {
        usdEntryFee = 50 * (10**18);
        ethPriceFeed = AggregatorV3Interface(_priceFeedAddress);
        lottery_state = LOTTERY_STATE.CLOSED;
        fee = _fee;
        keyhash = _keyhash;
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
        // uint256(
        //     keccak256(
        //         abi.encodePacked(
        //             nonce, // is predicatble ( number of transactions )
        //             msg.sender, // is predicatble
        //             block.difficulty, // can be manipulated by the miners
        //             block.timestamp // is predicatble
        //         )
        //     )
        // ) % players.length;
        lottery_state = LOTTERY_STATE.CALCULATING_WINNER;
        bytes32 requestId = requestRandomness(keyhash, fee);
    }

    function fulfillRandomness(bytes32 _requestId, uint256 _randomness)
        internal
        override
    {
        require(
            lottery_state == LOTTERY_STATE.CALCULATING_WINNER,
            "You are not there yet!"
        );
        require(_randomness > 0, "No random number");
        uint256 indexOfWinner = _randomness % players.length;
        recentWinner = players[indexOfWinner];
        recentWinner.transfer(address(this).balance);
        // Reset
        players = new address payable[](0);
        lottery_state = LOTTERY_STATE.CLOSED;
        randomness = _randomness;
    }
}
