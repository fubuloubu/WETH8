import pytest
from eip712.messages import EIP712Message


@pytest.fixture(scope="session")
def deployer(accounts):
    return accounts[-1]


@pytest.fixture(params=["WETH8", "WETH9", "WETH10", "METH_WETH"])
def weth(request, deployer, project):
    if request.param == "WETH8":
        # Use a type from our project
        weth_contract_type = project.WETH8

    else:
        # Use a type from a dependency
        dependency = list(project.dependencies.get(request.param.lower()).values())[0]
        weth_contract_type = dependency.get(request.param)

    if request.param == "METH_WETH":
        # NOTE: METH is set up to be deployed via some method involving CREATE2, so just hack it
        weth_contract_type.contract_type.deployment_bytecode.bytecode = (
            "0x600b80380380913d393df3"
            + weth_contract_type.contract_type.deployment_bytecode.bytecode[2:]
        )

    # Deploy a contract using our deployer
    return deployer.deploy(weth_contract_type)


@pytest.fixture
def Permit(chain, weth):
    class Permit(EIP712Message):
        _name_: "string" = weth.name()
        _version_: "string" = "1"
        _chainId_: "uint256" = chain.chain_id
        _verifyingContract_: "address" = weth.address

        owner: "address"
        spender: "address"
        value: "uint256"
        nonce: "uint256"
        deadline: "uint256"

    return Permit
