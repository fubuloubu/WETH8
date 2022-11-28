import WETH8 as WETH8

ERC3156_CALLBACK_SUCCESS: constant(bytes32) = keccak256("ERC3156FlashBorrower.onFlashLoan")


@external
def onFlashLoan(
    initiator: address,
    token: WETH8,
    amount: uint256,
    fee: uint256,
    data: Bytes[65535],
) -> bytes32:
    if len(data) >= 1 and convert(slice(data, 0, 1), bool):
        assert token.withdraw(amount)
        # NOTE: Don't deposit again, which should fail because it burns

    else:
        # NOTE: by default, try withdrawing and depositing again
        assert token.withdraw(amount)
        assert token.deposit(value=amount)

    return ERC3156_CALLBACK_SUCCESS


@payable
@external
def __default__():
    pass  # So withdrawal doesn't fail
