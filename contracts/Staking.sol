// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

import "./SafeMath.sol";
import "../interfaces/IERC20.sol";

contract Staking {
    using SafeMath for uint256;

    uint256 constant REWARD_STEP_COUNT = 2592000; // Number of steps for reward distribution

    IERC20 public ourToken;

    event Staked(address indexed user, uint256 amount);
    event Unstaked(address indexed user, uint256 amount);
    event RewardClaimed(address indexed user, uint256 amount);

    struct AmountHistory {
        uint256 amount;
        uint256 fromTimestamp;
        uint256 toTimestamp;
    }

    mapping(address => AmountHistory[]) userStakingHistory;
    
    AmountHistory[] rewardHistoryList;
    AmountHistory[] rewardPerTokenHistoryList;

    uint256 totalClaimedReward;
    uint256 public totalStakedBalance;
    uint256 public totalStakers;

    constructor(address _ourToken) {
        ourToken = IERC20(_ourToken);
    }


    function updateRewardPool() external {
        uint256 currentRewardBalance = ourToken.balanceOf(address(this)).sub(totalStakedBalance).add(totalClaimedReward);
        uint256 lastRewardBalance = 0;

        if (rewardHistoryList.length > 0) {
            lastRewardBalance = rewardHistoryList[rewardHistoryList.length - 1].amount;
        }

        if (currentRewardBalance > lastRewardBalance) {
            uint256 newBalance = currentRewardBalance.sub(lastRewardBalance);
            rewardHistoryList.push(AmountHistory(newBalance, block.timestamp, block.timestamp.add(REWARD_STEP_COUNT)));
            updateRewardPerToken();
        } else {
            revert("FailedToDetectNewRewardDeposit");
        }
    }

    function stake(uint256 amount) external {
        require(amount > 0, "Invalid amount");

        totalStakedBalance = totalStakedBalance.add(amount);

        uint256 lastUserStakedBalance = 0;

        if(userStakingHistory[msg.sender].length > 0){
            userStakingHistory[msg.sender][userStakingHistory[msg.sender].length - 1].toTimestamp = block.timestamp;
            lastUserStakedBalance = userStakingHistory[msg.sender][userStakingHistory[msg.sender].length - 1].amount;
        }

        uint256 newBalance = lastUserStakedBalance.add(amount);

        if(lastUserStakedBalance == 0 && newBalance > 0)
            totalStakers = totalStakers.add(1);

        userStakingHistory[msg.sender].push(AmountHistory(newBalance, block.timestamp, 0));
        
        updateRewardPerToken();

        bool result = ourToken.transferFrom(msg.sender, address(this), amount);
        require(result, "FailedToTransferToken");
        
        emit Staked(msg.sender, amount);
    }

    function unstake(uint256 amount) external {
        require(amount > 0, "Invalid amount");
        require(totalStakedBalance >= amount, "Invalid amount");

        totalStakedBalance = totalStakedBalance.sub(amount);

        uint256 lastUserStakedBalance = 0;

        if(userStakingHistory[msg.sender].length > 0){
            userStakingHistory[msg.sender][userStakingHistory[msg.sender].length - 1].toTimestamp = block.timestamp;
            lastUserStakedBalance = userStakingHistory[msg.sender][userStakingHistory[msg.sender].length - 1].amount;
        }

        require(lastUserStakedBalance >= amount, "InsufficientBalance");

        uint256 newBalance = lastUserStakedBalance.sub(amount);

        if(lastUserStakedBalance > 0 && newBalance == 0)
            totalStakers = totalStakers.sub(1);

        userStakingHistory[msg.sender].push(AmountHistory(lastUserStakedBalance.sub(amount), block.timestamp, 0));

        updateRewardPerToken();


        bool result = ourToken.transfer(msg.sender, amount);
        require(result, "FailedToTransferToken");

        emit Unstaked(msg.sender, amount);
    }

    function claimReward() external {
        uint256 availableReward = rewardBalance();
        require(availableReward > 0, "InsufficientBalance");

        totalClaimedReward = totalClaimedReward.add(availableReward);

        uint256 lastUserStakedBalance = 0;

        if (userStakingHistory[msg.sender].length > 0)
            lastUserStakedBalance = userStakingHistory[msg.sender][userStakingHistory[msg.sender].length - 1].amount;


        delete userStakingHistory[msg.sender];
        userStakingHistory[msg.sender].push(AmountHistory(lastUserStakedBalance, block.timestamp, 0));    

        
        bool result = ourToken.transfer(msg.sender, availableReward);
        require(result, "FailedToTransferToken");

        emit RewardClaimed(msg.sender, availableReward);
    }

    function stakeBalance(address user) external view returns (uint256) {
        uint256 balance = userStakingHistory[user].length > 0 ? userStakingHistory[user][userStakingHistory[user].length - 1].amount : 0;
        return balance;
    }

    function unallocatedRewardBalance() external view returns (uint256) {
        uint256 calculatedBalance = 0;
        for (uint256 i = 0; i < rewardHistoryList.length; i++) {
            AmountHistory storage reward = rewardHistoryList[i];
            if (reward.toTimestamp > block.timestamp){
                uint256 uallocatedStep = reward.toTimestamp.sub(block.timestamp);
                uint256 rewardPerStep = reward.amount.div(REWARD_STEP_COUNT);
                calculatedBalance += uallocatedStep.mul(rewardPerStep);
            }
                
        }
        return calculatedBalance;
    }

    function rewardBalance() public view returns (uint256) {
        uint256 calculatedReward = 0;

        for (uint256 i = 0; i < userStakingHistory[msg.sender].length; i++) {
            AmountHistory storage userHistory = userStakingHistory[msg.sender][i];
            uint256 userStartTime = userHistory.fromTimestamp;
            uint256 userEndTime = userHistory.toTimestamp > 0 ? userHistory.toTimestamp : block.timestamp;

            for (uint256 j = 0; j < rewardPerTokenHistoryList.length; j++) {
                AmountHistory storage rewardHistory = rewardPerTokenHistoryList[j];
                uint256 rewardStartTime = rewardHistory.fromTimestamp;
                uint256 rewardEndTime = rewardHistory.toTimestamp > 0 ? rewardHistory.toTimestamp : block.timestamp;
                
                if (rewardHistory.amount > 0 && (rewardStartTime < userEndTime || rewardEndTime > userStartTime)) {
                    uint256 endDuration = min(rewardEndTime, userEndTime);
                    uint256 startDuration = max(rewardStartTime, userStartTime);
                    
                    if (startDuration <= endDuration){
                        uint256 rewardDuration = endDuration.sub(startDuration);
                        calculatedReward = calculatedReward.add(rewardDuration.mul(rewardHistory.amount).mul(userHistory.amount.div(1e18)));
                    }
                }
            }
        }

        return calculatedReward;
    }

    function calculateRewardPerToken() public view returns (uint256) {
        uint256 rewardRatePerStep = 0;

        for (uint256 i = 0; i < rewardHistoryList.length; i++) {
            if (rewardHistoryList[i].toTimestamp > block.timestamp && totalStakedBalance > 0) {
                rewardRatePerStep = rewardRatePerStep.add(rewardHistoryList[i].amount.div(REWARD_STEP_COUNT).div(totalStakedBalance.div(1e18)));
            }
        }

        return rewardRatePerStep;
    }

    function max(uint256 a, uint256 b) private pure returns (uint256) {
        return a >= b ? a : b;
    }

    function min(uint256 a, uint256 b) private pure returns (uint256) {
        return a <= b ? a : b;
    }


    function updateRewardPerToken() private {
        if(rewardPerTokenHistoryList.length > 0)
            rewardPerTokenHistoryList[rewardPerTokenHistoryList.length - 1].toTimestamp = block.timestamp;

        rewardPerTokenHistoryList.push(AmountHistory(calculateRewardPerToken(), block.timestamp, 0));
    }
}
