#!/usr/bin/python3

from brownie import Staking, accounts


def main():
    print(accounts)
    return Staking.deploy("",{'from': accounts.load("bscMainPrivate")},  publish_source=True)