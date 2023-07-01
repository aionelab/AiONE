import brownie
from web3 import Web3

def test_stake_with_approve(staking, token, accounts):
    assert staking.stakeBalance(accounts[0]) == 0
    assert staking.totalStakedBalance() == 0
    assert staking.totalStakers() == 0

    tx = token.approve(staking.address, Web3.toWei( 100 ,'ether'), {'from': accounts[0]})
    tx.wait(1)

    tx = staking.stake(Web3.toWei( 100 ,'ether'), {'from': accounts[0]})
    tx.wait(1)

    assert staking.stakeBalance(accounts[0]) == Web3.toWei( 100 ,'ether')
    assert staking.totalStakedBalance() == Web3.toWei( 100 ,'ether')
    assert staking.totalStakers() == 1


def test_stake_without_approve(staking, token, accounts):
    assert staking.stakeBalance(accounts[0]) == 0

    with brownie.reverts():
        staking.stake(Web3.toWei( 100 ,'ether'), {'from': accounts[0]})

def test_stake_zero(staking, token, accounts):
    assert staking.stakeBalance(accounts[0]) == 0

    tx = token.approve(staking.address, Web3.toWei( 100 ,'ether'), {'from': accounts[0]})
    tx.wait(1)
    
    with brownie.reverts():
        staking.stake(Web3.toWei( 0 ,'ether'), {'from': accounts[0]})


def test_stake_without_balance(staking, token, accounts):
    assert staking.stakeBalance(accounts[1]) == 0

    tx = token.approve(staking.address, Web3.toWei( 100 ,'ether'), {'from': accounts[1]})
    tx.wait(1)

    with brownie.reverts():
        staking.stake(Web3.toWei( 100 ,'ether'), {'from': accounts[0]})


def test_increase_stake(staking, token, accounts):
    tx = token.approve(staking.address, Web3.toWei( 100 ,'ether'), {'from': accounts[0]})
    tx.wait(1)

    tx = staking.stake(Web3.toWei( 100 ,'ether'), {'from': accounts[0]})
    tx.wait(1)

    tx = token.approve(staking.address, Web3.toWei( 100 ,'ether'), {'from': accounts[0]})
    tx.wait(1)

    tx = staking.stake(Web3.toWei( 100 ,'ether'), {'from': accounts[0]})
    tx.wait(1)


    assert staking.stakeBalance(accounts[0]) == Web3.toWei( 200 ,'ether')
    assert staking.totalStakedBalance() == Web3.toWei( 200 ,'ether')
    assert staking.totalStakers() == 1


def test_multiple_staker(staking, token, accounts):
    assert staking.totalStakedBalance() == 0
    assert staking.totalStakers() == 0
    
    tx = token.approve(staking.address, Web3.toWei( 100 ,'ether'), {'from': accounts[0]})
    tx.wait(1)

    tx = staking.stake(Web3.toWei( 100 ,'ether'), {'from': accounts[0]})
    tx.wait(1)

    assert staking.totalStakedBalance() == Web3.toWei( 100 ,'ether')
    assert staking.totalStakers() == 1

    tx = token.transfer(accounts[1], Web3.toWei( 150 ,'ether'), {'from': accounts[0]})
    tx.wait(1)

    tx = token.approve(staking.address, Web3.toWei( 150 ,'ether'), {'from': accounts[1]})
    tx.wait(1)

    tx = staking.stake(Web3.toWei( 150 ,'ether'), {'from': accounts[1]})
    tx.wait(1)


    assert staking.stakeBalance(accounts[1]) == Web3.toWei( 150 ,'ether')
    assert staking.totalStakedBalance() == Web3.toWei( 250 ,'ether')
    assert staking.totalStakers() == 2
