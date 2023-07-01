import brownie
from web3 import Web3

def test_unstake_all(staking, token, accounts):
    tx = token.approve(staking.address, Web3.toWei( 100 ,'ether'), {'from': accounts[0]})
    tx.wait(1)

    tx = staking.stake(Web3.toWei( 100 ,'ether'), {'from': accounts[0]})
    tx.wait(1)
    balance = token.balanceOf(accounts[0])

    assert staking.stakeBalance(accounts[0]) == Web3.toWei( 100 ,'ether')
    assert staking.totalStakedBalance() == Web3.toWei( 100 ,'ether')
    assert staking.totalStakers() == 1

    tx = staking.unstake(Web3.toWei( 100 ,'ether'), {'from': accounts[0]})
    tx.wait(1)

    assert balance + Web3.toWei( 100 ,'ether') == token.balanceOf(accounts[0])

    assert staking.stakeBalance(accounts[0]) ==0
    assert staking.totalStakedBalance() == 0
    assert staking.totalStakers() == 0


def test_unstake_part_of_balance(staking, token, accounts):
    tx = token.approve(staking.address, Web3.toWei( 100 ,'ether'), {'from': accounts[0]})
    tx.wait(1)

    tx = staking.stake(Web3.toWei( 100 ,'ether'), {'from': accounts[0]})
    tx.wait(1)
    balance = token.balanceOf(accounts[0])

    assert staking.stakeBalance(accounts[0]) == Web3.toWei( 100 ,'ether')
    assert staking.totalStakedBalance() == Web3.toWei( 100 ,'ether')
    assert staking.totalStakers() == 1

    tx = staking.unstake(Web3.toWei( 50 ,'ether'), {'from': accounts[0]})
    tx.wait(1)

    assert balance + Web3.toWei( 50 ,'ether') == token.balanceOf(accounts[0])

    assert staking.stakeBalance(accounts[0]) == Web3.toWei( 50 ,'ether')
    assert staking.totalStakedBalance() == Web3.toWei( 50 ,'ether')
    assert staking.totalStakers() == 1


def test_unstake_zero(staking, token, accounts):
    tx = token.approve(staking.address, Web3.toWei( 100 ,'ether'), {'from': accounts[0]})
    tx.wait(1)

    tx = staking.stake(Web3.toWei( 100 ,'ether'), {'from': accounts[0]})
    tx.wait(1)

    balance = token.balanceOf(accounts[0])

    tx = token.approve(staking.address, Web3.toWei( 100 ,'ether'), {'from': accounts[0]})
    tx.wait(1)
    
    with brownie.reverts():
        staking.stake(Web3.toWei( 0 ,'ether'), {'from': accounts[0]})


def test_unstake_without_balance(staking, token, accounts):
    tx = token.approve(staking.address, Web3.toWei( 100 ,'ether'), {'from': accounts[0]})
    tx.wait(1)

    tx = staking.stake(Web3.toWei( 100 ,'ether'), {'from': accounts[0]})
    tx.wait(1)
    
    balance = token.balanceOf(accounts[0])

    tx = token.approve(staking.address, Web3.toWei( 100 ,'ether'), {'from': accounts[0]})
    tx.wait(1)
    
    with brownie.reverts():
        staking.stake( Web3.toWei( 100 ,'ether') + 1, {'from': accounts[0]})


def test_unstake_all_with_multiple_user(staking, token, accounts):
    tx = token.transfer(accounts[1], Web3.toWei( 100 ,'ether'), {'from': accounts[0]})
    tx.wait(1)

    tx = token.approve(staking.address, Web3.toWei( 100 ,'ether'), {'from': accounts[0]})
    tx.wait(1)

    tx = staking.stake(Web3.toWei( 100 ,'ether'), {'from': accounts[0]})
    tx.wait(1)

    tx = token.approve(staking.address, Web3.toWei( 100 ,'ether'), {'from': accounts[1]})
    tx.wait(1)

    tx = staking.stake(Web3.toWei( 100 ,'ether'), {'from': accounts[1]})
    tx.wait(1)

    balance = token.balanceOf(accounts[0])

    assert staking.stakeBalance(accounts[0]) == Web3.toWei( 100 ,'ether')
    assert staking.stakeBalance(accounts[1]) == Web3.toWei( 100 ,'ether')
    assert staking.totalStakedBalance() == Web3.toWei( 200 ,'ether')
    assert staking.totalStakers() == 2

    tx = staking.unstake(Web3.toWei( 100 ,'ether'), {'from': accounts[0]})
    tx.wait(1)

    assert balance + Web3.toWei( 100 ,'ether') == token.balanceOf(accounts[0])

    assert staking.stakeBalance(accounts[0]) == Web3.toWei( 0 ,'ether')
    assert staking.stakeBalance(accounts[1]) == Web3.toWei( 100 ,'ether')
    assert staking.totalStakedBalance() == Web3.toWei( 100 ,'ether')
    assert staking.totalStakers() == 1