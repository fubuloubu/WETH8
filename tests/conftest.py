import pytest


@pytest.fixture(scope="session")
def deployer(accounts):
    return accounts[-1]


@pytest.fixture(params=["WETH8", "WETH9", "WETH10"])
def weth(request, deployer, project):
    if request.param == "WETH8":
        # Use a type from our project
        weth_contract_type = project.WETH8

    else:
        # Use a type from a dependency
        dependency = list(project.dependencies.get(request.param.lower()).values())[0]
        weth_contract_type = dependency.get(request.param)

    # Deploy a contract using our deployer
    return deployer.deploy(weth_contract_type)
