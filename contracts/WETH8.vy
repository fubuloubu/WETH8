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

# EIP-2612
nonces: public(HashMap[address, uint256])
DOMAIN_SEPARATOR: public(bytes32)
DOMAIN_TYPE_HASH: constant(bytes32) = keccak256(
    "EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"
)
PERMIT_TYPE_HASH: constant(bytes32) = keccak256(
    "Permit(address owner,address spender,uint256 value,uint256 nonce,uint256 deadline)"
)


@external
def __init__():
    # EIP-2612
    self.DOMAIN_SEPARATOR = keccak256(
        concat(
            DOMAIN_TYPE_HASH,
            keccak256(name),
            keccak256("1"),
            _abi_encode(chain.id, self)
        )
    )


@view
@external
def totalSupply() -> uint256:
    return self.balance


@external
def transfer(receiver: address, amount: uint256) -> bool:
    assert receiver not in [empty(address), self]

    self.balanceOf[msg.sender] -= amount
    # NOTE: `unsafe_add` is safe here because there is a limited amount of ether <<< max(uint256)
    self.balanceOf[receiver] = unsafe_add(self.balanceOf[receiver], amount)

    log Transfer(msg.sender, receiver, amount)
    return True


@external
def transferFrom(sender: address, receiver: address, amount: uint256) -> bool:
    assert receiver not in [empty(address), self]

    self.allowance[sender][msg.sender] -= amount
    self.balanceOf[sender] -= amount
    # NOTE: `unsafe_add` is safe here because of total supply invariant
    self.balanceOf[receiver] = unsafe_add(self.balanceOf[receiver], amount)

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
    # NOTE: totalSupply decreases here by `amount`
    self.balanceOf[owner] -= amount
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
    # NOTE: totalSupply increases here by `amount`
    # NOTE: `unsafe_add` is safe here because there is a limited amount of ether <<< max(uint256)
    self.balanceOf[receiver] = unsafe_add(self.balanceOf[receiver], amount)
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


# EIP-2612
@external
def permit(
    owner: address,
    spender: address,
    amount: uint256,
    expiry: uint256,
    v: uint256,
    r: bytes32,
    s: bytes32,
) -> bool:
    """
    @notice
        Approves spender by owner's signature to expend owner's tokens.
        See https://eips.ethereum.org/EIPS/eip-2612.
    @param owner The address which is a source of funds and has signed the Permit.
    @param spender The address which is allowed to spend the funds.
    @param amount The amount of tokens to be spent.
    @param expiry The timestamp after which the Permit is no longer valid.
    @param v V parameter of secp256k1 signature for Permit by owner.
    @param r R parameter of secp256k1 signature for Permit by owner.
    @param s S parameter of secp256k1 signature for Permit by owner.
    @return A boolean that indicates if the operation was successful.
    """
    assert owner != empty(address)  # dev: invalid owner
    assert expiry == 0 or expiry >= block.timestamp  # dev: permit expired
    nonce: uint256 = self.nonces[owner]
    digest: bytes32 = keccak256(
        concat(
            b'\x19\x01',
            self.DOMAIN_SEPARATOR,
            keccak256(
                _abi_encode(
                    PERMIT_TYPE_HASH,
                    owner,
                    spender,
                    amount,
                    nonce,
                    expiry,
                )
            )
        )
    )

    assert ecrecover(digest, v, r, s) == owner  # dev: invalid signature

    self.allowance[owner][spender] = amount
    self.nonces[owner] = nonce + 1

    log Approval(owner, spender, amount)
    return True
