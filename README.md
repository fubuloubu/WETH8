# Wrapped Ether (WETH8)

This experiment updates the canonical ["Wrapped Ether" WETH(9) contract](https://etherscan.io/address/0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2#code)
by implementing it in modern Vyper with several improvements for gas savings purposes.
We also compare it to the [WETH(10)](https://github.com/WETH10/WETH10) project as another attempt to make an upgrade to WETH(9).

## Wrapping Ether

Any operation that ends with this contract holding Wrapped Ether is prohibited.

`deposit` Ether in this contract to receive Wrapped Ether (WETH), which implements the ERC20 standard. WETH is interchangeable with Ether in a 1:1 basis.

`withdraw` Ether from this contract by unwrapping WETH from your wallet.

## Approvals

When an account's `allowance` is set to `max(uint256)` it will not decrease through `transferFrom` or `withdrawFrom` calls.

WETH10 implements EIP2612 to set approvals through off-chain signatures.

## Why WETH(8)?

The original WETH(9) contract uses "Kelvin Versioning", which is a unique way to do software versioning such that versions start at a high number
and count down to version 0, at which point the software is considered finished and no further modifications are made.
In the spirit of that original, we are decrementing this number by 1 to indicate the level of progress this implementation is making towards a
final, more immutable copy.

## Deployments

This contract is deployed on Goerli at: [0xD2082D10e36b169f4F2331867dcc1A719297037e](https://goerli.etherscan.io/address/0xd2082d10e36b169f4f2331867dcc1a719297037e)

## Credits

This project draws singificant inspiration from WETH(10) both in terms of goals and several of the upgrades that are applied.

Generated from [Token template](https://github.com/ApeAcademy/ERC20) by [Ape Academy](https://academy.apeworx.io)
