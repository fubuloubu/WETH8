# @version 0.3.7
"""
@title WETH8
@license MIT
@author ApeWorX Ltd.
@notice Vyper implementation of the WETH9 contract + ERC2612 + ERC3156
"""

from vyper.interfaces import ERC20


implements: ERC20

# ERC20 Token Metadata
name: public(constant(String[20])) = "Wrapped Ether"
symbol: public(constant(String[5])) = "WETH"
decimals: public(constant(uint8)) = 18

# ERC20 State Variables
totalSupply: public(uint256)
balanceOf: public(HashMap[address, uint256])
allowance: public(HashMap[address, HashMap[address, uint256]])

# ERC20 Events
event Transfer:
    sender: indexed(address)
    receiver: indexed(address)
    amount: uint256

event Approval:
    owner: indexed(address)
    spender: indexed(address)
    amount: uint256


@external
def transfer(receiver: address, amount: uint256) -> bool:
    assert receiver not in [empty(address), self]

    self.balanceOf[msg.sender] -= amount
    self.balanceOf[receiver] += amount

    log Transfer(msg.sender, receiver, amount)
    return True


@external
def transferFrom(sender: address, receiver: address, amount: uint256) -> bool:
    assert receiver not in [empty(address), self]

    self.allowance[sender][msg.sender] -= amount
    self.balanceOf[sender] -= amount
    self.balanceOf[receiver] += amount

    log Transfer(sender, receiver, amount)
    return True


@external
def approve(spender: address, amount: uint256) -> bool:
    """
    @param spender The address that will execute on owner behalf.
    @param amount The amount of token to be transfered.
    @return A boolean that indicates if the operation was successful.
    """
    self.allowance[msg.sender][spender] = amount

    log Approval(msg.sender, spender, amount)
    return True


@internal
def _burn(owner: address, amount: uint256):
    self.balanceOf[owner] -= amount
    self.totalSupply -= amount
    log Transfer(owner, empty(address), amount)


@external
def withdraw(amount: uint256) -> bool:
    """
    @notice Burns the supplied amount of tokens from the sender wallet.
    @param amount The amount of token to be burned.
    @return A boolean that indicates if the operation was successful.
    """
    self._burn(msg.sender, amount)
    send(msg.sender, amount)
    return True


@internal
def _mint(receiver: address, amount: uint256):
    self.totalSupply += amount
    self.balanceOf[receiver] += amount
    log Transfer(empty(address), receiver, amount)


@payable
@external
def deposit() -> bool:
    """
    @notice Function to mint tokens
    @return A boolean that indicates if the operation was successful.
    """
    self._mint(msg.sender, msg.value)
    return True


@payable
@external
def __default__():
    self._mint(msg.sender, msg.value)
