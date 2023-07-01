import brownie
from web3 import Web3

def test_reward_change_and_claim(staking, token, accounts):
    tx = token.transfer(staking.address, Web3.toWei( 2592000 ,'ether'), {'from': accounts[0]})
    tx.wait(1)

    tx = token.approve(staking.address, Web3.toWei( 100 ,'ether'), {'from': accounts[0]})
    tx.wait(1)

    tx = staking.stake(Web3.toWei( 100 ,'ether'), {'from': accounts[0]})
    tx.wait(1)

    assert staking.calculateRewardPerToken() == 0
    balance = token.balanceOf(accounts[0])

    tx = staking.updateRewardPool({'from': accounts[0]})
    tx.wait(1)

    assert staking.calculateRewardPerToken() == Web3.toWei( 0.01 ,'ether')

    brownie.chain.sleep(100000)

    tx = staking.claimReward({'from': accounts[0]})
    tx.wait(1)
    
    new_assert_balance = balance + Web3.toWei( 100000 ,'ether')
    assert token.balanceOf(accounts[0]) == new_assert_balance

    tx = token.transfer(staking.address, Web3.toWei( 2592000 ,'ether'), {'from': accounts[0]})
    tx.wait(1)

    tx = staking.updateRewardPool({'from': accounts[0]})
    tx.wait(1)

    assert staking.calculateRewardPerToken() == Web3.toWei( 0.02 ,'ether')
    assert staking.unallocatedRewardBalance() == Web3.toWei( 2492000 ,'ether') + Web3.toWei(2592000 ,'ether') 



def test_claim_reward_change_rate(staking, token, accounts):
    tx = token.transfer(accounts[1], Web3.toWei( 900 ,'ether'), {'from': accounts[0]})
    tx.wait(1)

    tx = token.approve(staking.address, Web3.toWei( 900 ,'ether'), {'from': accounts[1]})
    tx.wait(1)

    tx = token.transfer(staking.address, Web3.toWei( 2592000 ,'ether'), {'from': accounts[0]})
    tx.wait(1)

    tx = token.approve(staking.address, Web3.toWei( 100 ,'ether'), {'from': accounts[0]})
    tx.wait(1)

    tx = staking.stake(Web3.toWei( 100 ,'ether'), {'from': accounts[0]})
    tx.wait(1)

    assert staking.calculateRewardPerToken() == 0
    balance = token.balanceOf(accounts[0])

    tx = staking.updateRewardPool({'from': accounts[0]})
    tx.wait(1)

    assert staking.calculateRewardPerToken() == Web3.toWei( 0.01 ,'ether')

    brownie.chain.sleep(50000)

    tx = staking.stake(Web3.toWei( 900 ,'ether'), {'from': accounts[1]})
    tx.wait(1)

    assert staking.calculateRewardPerToken() == Web3.toWei( 0.001 ,'ether')

    brownie.chain.sleep(50000)

    tx = staking.claimReward({'from': accounts[0]})
    tx.wait(1)

    new_assert_balance = balance + Web3.toWei( 55000 ,'ether')
    assert token.balanceOf(accounts[0]) == new_assert_balance
    

def test_claim_ward_change_stake(staking, token, accounts):
    tx = token.transfer(staking.address, Web3.toWei( 2592000 ,'ether'), {'from': accounts[0]})
    tx.wait(1)

    tx = token.approve(staking.address, Web3.toWei( 100 ,'ether'), {'from': accounts[0]})
    tx.wait(1)

    tx = staking.stake(Web3.toWei( 100 ,'ether'), {'from': accounts[0]})
    tx.wait(1)

    assert staking.calculateRewardPerToken() == 0
    balance = token.balanceOf(accounts[0])

    tx = staking.updateRewardPool({'from': accounts[0]})
    tx.wait(1)

    assert staking.calculateRewardPerToken() == Web3.toWei( 0.01 ,'ether')

    brownie.chain.sleep(50000)
    
    tx = staking.unstake(Web3.toWei( 90 ,'ether'), {'from': accounts[0]})
    tx.wait(1)
    
    assert staking.calculateRewardPerToken() == Web3.toWei( 0.1 ,'ether')
    brownie.chain.sleep(50000)

    tx = staking.claimReward({'from': accounts[0]})
    tx.wait(1)

    new_assert_balance = balance + Web3.toWei( 100000 ,'ether') + Web3.toWei( 90 ,'ether')
    assert token.balanceOf(accounts[0]) == new_assert_balance
