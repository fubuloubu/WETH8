import ape
import pytest


@pytest.fixture
def borrower(project, deployer):
    return deployer.deploy(project.TestFlashReceiver)


def test_max_flash(weth, accounts):
    if weth.contract_type.name in ("WETH9", "METH_WETH"):
        pytest.skip(f"{weth.contract_type.name} doesn't support ERC-3156")

    caller = accounts[0]

    if weth.contract_type.name == "WETH10":
        assert weth.maxFlashLoan(weth) == (2**112 - 1)  # Static value for maximum

    else:
        assert weth.maxFlashLoan(weth) == 0

        weth.deposit(sender=caller, value="1 ether")

        assert weth.maxFlashLoan(weth) == int(1e16)  # 0.01 ether

    # Says 0 with any address that isn't `weth`
    weth.maxFlashLoan(caller) == 0


def test_flash_fee(weth, accounts):
    if weth.contract_type.name in ("WETH9", "METH_WETH"):
        pytest.skip(f"{weth.contract_type.name} doesn't support ERC-3156")

    caller = accounts[0]

    with ape.reverts():
        # Fails with any address that isn't `weth`
        weth.flashFee(caller, "1 ether")

    # NOTE: Always no fee
    assert weth.flashFee(weth, "1 ether") == 0


def test_flash_loan(weth, borrower, accounts):
    if weth.contract_type.name in ("WETH9", "METH_WETH"):
        pytest.skip(f"{weth.contract_type.name} doesn't support ERC-3156")

    caller = accounts[0]

    with ape.reverts():
        # Fails because no balance
        weth.flashLoan(borrower, weth, "0.01 ether", b"", sender=caller)

    weth.deposit(sender=caller, value="1 ether")

    with ape.reverts():
        # Fails because caller doesn't return anything
        weth.flashLoan(caller, weth, "0.01 ether", b"", sender=caller)

    with ape.reverts():
        # Fails because caller doesn't have any WETH to give back
        # NOTE: nonzero first byte means withdraw but don't deposit
        weth.flashLoan(caller, weth, "0.01 ether", b"\x01", sender=caller)

    with ape.reverts():
        # Fails because trying to balance more than available
        weth.flashLoan(borrower, weth, "0.011 ether", b"", sender=caller)

    if weth.contract_type.name == "WETH10":
        # NOTE: WETH10 requires that the borrower approve the weth account for returning tokens
        weth.approve(weth, "0.01 ether", sender=borrower)

    weth.flashLoan(borrower, weth, "0.01 ether", b"", sender=caller)
