import ape
import pytest


def test_permit(chain, weth, accounts, Permit):
    if weth.contract_type.name == "WETH9":
        pytest.skip("WETH9 doesn't support ERC-2612")

    owner, spender = accounts[:2]

    amount = 100
    nonce = weth.nonces(owner)
    deadline = chain.pending_timestamp + 60
    assert weth.allowance(owner, spender) == 0
    permit = Permit(owner.address, spender.address, amount, nonce, deadline)
    signature = owner.sign_message(permit.signable_message)
    v, r, s = signature.v, signature.r, signature.s

    with ape.reverts():
        weth.permit(spender, spender, amount, deadline, v, r, s, sender=spender)
    with ape.reverts():
        weth.permit(owner, owner, amount, deadline, v, r, s, sender=spender)
    with ape.reverts():
        weth.permit(owner, spender, amount + 1, deadline, v, r, s, sender=spender)
    with ape.reverts():
        weth.permit(owner, spender, amount, deadline + 1, v, r, s, sender=spender)

    tx = weth.permit(owner, spender, amount, deadline, v, r, s, sender=spender)

    assert weth.allowance(owner, spender) == 100

    logs = list(tx.decode_logs(weth.Approval))
    assert len(logs) == 1
    src, guy, amt = logs[0].event_arguments.values()
    assert src == owner
    assert guy == spender
    assert amt == 100
