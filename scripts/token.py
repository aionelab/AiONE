#!/usr/bin/python3

from brownie import Token, accounts


def main():
    print(accounts)
    return Token.deploy({'from': accounts.load("bscMainPrivate")},  publish_source=True)