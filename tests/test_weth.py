import ape
from ape import convert

# Standard test comes from the interpretation of EIP-20
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
ONE_ETHER = convert("1 ether", int)


def test_initial_state(weth):
    if weth.contract_type.name == "WETH10":
        assert weth.name() == "Wrapped Ether v10"
        assert weth.symbol() == "WETH10"
    else:
        assert weth.name() == "Wrapped Ether"
        assert weth.symbol() == "WETH"

    assert weth.decimals() == 18
    assert weth.totalSupply() == 0


def test_deposit_by_call(weth, accounts):
    owner = accounts[0]
    bal_before = owner.balance

    tx = weth.deposit(sender=owner, value="1 ether")

    assert weth.balance == ONE_ETHER
    # assert owner.balance == bal_before - ONE_ETHER
    assert weth.balanceOf(owner) == ONE_ETHER
    assert weth.totalSupply() == ONE_ETHER

    if weth.contract_type.name == "WETH9":
        logs = list(tx.decode_logs(weth.Deposit))
        assert len(logs) == 1
        assert logs[0].dst == owner
        assert logs[0].wad == ONE_ETHER

    else:
        logs = list(tx.decode_logs(weth.Transfer))
        assert len(logs) == 1
        sender, receiver, amount = logs[0].event_arguments.values()
        assert sender == ZERO_ADDRESS
        assert receiver == owner
        assert amount == ONE_ETHER


def test_deposit_by_send(weth, accounts):
    owner = accounts[0]
    bal_before = owner.balance

    tx = owner.transfer(weth, "1 ether")

    assert weth.balance == ONE_ETHER
    # assert owner.balance == bal_before - ONE_ETHER
    assert weth.balanceOf(owner) == ONE_ETHER
    assert weth.totalSupply() == ONE_ETHER

    if weth.contract_type.name == "WETH9":
        logs = list(tx.decode_logs(weth.Deposit))
        assert len(logs) == 1
        assert logs[0].dst == owner
        assert logs[0].wad == ONE_ETHER

    else:
        logs = list(tx.decode_logs(weth.Transfer))
        assert len(logs) == 1
        sender, receiver, amount = logs[0].event_arguments.values()
        assert sender == ZERO_ADDRESS
        assert receiver == owner
        assert amount == ONE_ETHER


def test_withdraw(weth, accounts):
    owner = accounts[0]
    bal_before = owner.balance

    weth.deposit(sender=owner, value="1 ether")

    tx = weth.withdraw(ONE_ETHER, sender=owner)

    assert weth.balance == 0
    # assert owner.balance == bal_before
    assert weth.balanceOf(owner) == 0
    assert weth.totalSupply() == 0

    if weth.contract_type.name == "WETH9":
        logs = list(tx.decode_logs(weth.Withdrawal))
        assert len(logs) == 1
        assert logs[0].src == owner
        assert logs[0].wad == ONE_ETHER

    else:
        logs = list(tx.decode_logs(weth.Transfer))
        assert len(logs) == 1
        src, dst, amt = logs[0].event_arguments.values()
        assert src == owner
        assert dst == ZERO_ADDRESS
        assert amt == ONE_ETHER


def test_transfer(weth, accounts):
    owner, receiver = accounts[:2]
    weth.deposit(sender=owner, value="1 ether")

    tx = weth.transfer(receiver, 100, sender=owner)

    assert weth.balance == ONE_ETHER
    assert weth.totalSupply() == ONE_ETHER
    assert weth.balanceOf(receiver) == 100
    assert weth.balanceOf(owner) == ONE_ETHER - 100

    logs = list(tx.decode_logs(weth.Transfer))
    assert len(logs) == 1
    src, dst, amt = logs[0].event_arguments.values()
    assert src == owner
    assert dst == receiver
    assert amt == 100

    # Expected insufficient funds failure
    with ape.reverts():
        weth.transfer(owner, 101, sender=receiver)

    # NOTE: Transfers of 0 values MUST be treated as normal transfers
    weth.transfer(owner, 0, sender=owner)


def test_approve(weth, accounts):
    owner, spender = accounts[:2]
    tx = weth.approve(spender, 300, sender=owner)

    assert weth.allowance(owner, spender) == 300

    logs = list(tx.decode_logs(weth.Approval))
    assert len(logs) == 1
    src, guy, amt = logs[0].event_arguments.values()
    assert src == owner
    assert guy == spender
    assert amt == 300


def test_transfer_from(weth, accounts):
    owner, receiver, spender = accounts[:3]
    weth.deposit(sender=owner, value="1 ether")

    # Spender with no approve permission cannot send weths on someone behalf
    with ape.reverts():
        weth.transferFrom(owner, receiver, 300, sender=spender)

    # Get approval for allowance from owner
    weth.approve(spender, 300, sender=owner)

    # With auth use the allowance to send to receiver via spender(operator)
    tx = weth.transferFrom(owner, receiver, 200, sender=spender)

    assert weth.balance == ONE_ETHER
    assert weth.allowance(owner, spender) == 100

    logs = list(tx.decode_logs(weth.Transfer))
    assert len(logs) == 1
    sender, receiver, amount = logs[0].event_arguments.values()
    assert sender == owner
    assert receiver == receiver
    assert amount == 200

    # Cannot exceed authorized allowance
    with ape.reverts():
        weth.transferFrom(owner, receiver, 200, sender=spender)

    # If approval reset, can't spend anymore
    weth.approve(spender, 0, sender=owner)
    with ape.reverts():
        weth.transferFrom(owner, receiver, 100, sender=spender)
