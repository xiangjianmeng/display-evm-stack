from brownie.network.web3 import web3
from network.transaction import TransactionReceipt, _get_memory
from brownie import project
import json
import warnings
from pathlib import Path
import brownie.convert.utils as utils
from typing import Any, Dict, Iterator, List, Match, Optional, Set, Tuple, Union
from hexbytes import HexBytes
from brownie.convert import EthAddress, Wei
from brownie.network.contract import _ContractMethod, OverloadedMethod, ContractCall, ContractTx
from eth_abi import decode_abi
from brownie.typing import AccountsType
from brownie.exceptions import BrownieEnvironmentWarning

addr_to_contract: Dict = {}


class Contract:

    def __init__(self, address: EthAddress, abi: Dict = None, sources: Dict = None) -> None:
        self._sources = sources
        self.abi = abi
        self.address = address
        self.selectors = None
        self.signatures = None
        if self.abi != None:
            self.selectors = {
                utils.build_function_selector(i): i["name"] for i in self.abi if i["type"] == "function"
            }
            # this isn't fully accurate because of overloaded methods - will be removed in `v2.0.0`
            self.signatures = {
                i["name"]: utils.build_function_selector(i) for i in self.abi if i["type"] == "function"
            }

            fn_names = [i["name"] for i in self.abi if i["type"] == "function"]
            for abi in [i for i in self.abi if i["type"] == "function"]:
                name = f"{self.address}.{abi['name']}"
                natspec: Dict = {}
                if fn_names.count(abi["name"]) == 1:
                    fn = _get_method_object(address, abi, name, None, natspec)
                    self._check_and_set(abi["name"], fn)
                    continue

                # special logic to handle function overloading
                if not hasattr(self, abi["name"]):
                    overloaded = OverloadedMethod(address, name, None)
                    self._check_and_set(abi["name"], overloaded)
                getattr(self, abi["name"])._add_fn(abi, natspec)

    def get_method(self, calldata: str) -> Optional[str]:
        sig = calldata[:10].lower()
        if self.selectors != None:
            return self.selectors.get(sig)
        else:
            return sig

    def get_method_object(self, calldata: str) -> Optional["_ContractMethod"]:
        """
        Given a calldata hex string, returns a `ContractMethod` object.
        """
        sig = calldata[:10].lower()
        if self.selectors != None:
            if sig not in self.selectors:
                return None
            fn = getattr(self, self.selectors[sig], None)
            if isinstance(fn, OverloadedMethod):
                return next((v for v in fn.methods.values() if v.signature == sig), None)
            return fn

    def _check_and_set(self, name: str, obj: Any) -> None:
        if name == "balance":
            warnings.warn(
                f"'{self.address}' defines a 'balance' function, "
                f"'{self.address}.balance' is unavailable",
                BrownieEnvironmentWarning,
            )
        elif hasattr(self, name):
            raise AttributeError(f"Namespace collision: '{self.address}.{name}'")
        setattr(self, name, obj)


def _get_method_object(
    address: str, abi: Dict, name: str, owner: Optional[AccountsType], natspec: Dict
) -> Union["ContractCall", "ContractTx"]:

    if "constant" in abi:
        constant = abi["constant"]
    else:
        constant = abi["stateMutability"] in ("view", "pure")

    if constant:
        return ContractCall(address, abi, name, owner, natspec)
    return ContractTx(address, abi, name, owner, natspec)


def _get_last_map(address, sig: str) -> Dict:
    contract = addr_to_contract[address]
    if contract == None:
        # TODO: load abi from explorer
        return

    last_map = {"address": EthAddress(address), "jumpDepth": 0, "coverage": False}

    if contract:
        if contract.get_method(sig):
            full_fn_name = f"{contract.address}.{contract.get_method(sig)}"
        else:
            full_fn_name = contract.address
        last_map.update(
            contract=contract,
            function=contract.get_method_object(sig),
            internal_calls=[full_fn_name],
            # pc_map=contract._build.get("pcMap"),
        )
        # only evaluate coverage for contracts that are part of a `Project`
        last_map["coverage"] = True
        # if contract._build["language"] == "Solidity":
        #     last_map["active_branches"] = set()
        last_map["active_branches"] = set()
    else:
        last_map.update(contract=None, internal_calls=[f"<UnknownContract>.{sig}"], pc_map=None)

    return last_map


if __name__ == '__main__':
    # web3.connect("http://okexchaintest-rpc2.okexcn.com:26659")
    web3.connect("http://127.0.0.1:8545")
    txhash = "0x9451efb3820851d5110a3b61cd4886916cc3fa6669487b18f98a1fa48f37696c"

    build = Path(__file__).parent.joinpath("build/contracts")

    with open(build.joinpath("test1.abi")) as json_file:
        test1abi = json.load(json_file)

    with open(build.joinpath("test2.abi")) as json_file:
        test2abi = json.load(json_file)

    addr_to_contract["0x1d29789a81aa381fE5830cd378Bb8F5c76E8C8a7"] = Contract(EthAddress("0x1d29789a81aa381fE5830cd378Bb8F5c76E8C8a7"), test1abi)
    addr_to_contract["0x0d021d10ab9E155Fc1e8705d12b73f9bd3de0a36"] = Contract(EthAddress("0x0d021d10ab9E155Fc1e8705d12b73f9bd3de0a36"), test2abi)

    tracesPath = Path(__file__).parent.joinpath("traces")

    # display all verified contract call stack
    # so it's impossible to display the stack of deploying a contract
    receipt = TransactionReceipt(
        txhash,
    )

    with open(tracesPath.joinpath(txhash)) as json_file:
        trace = json.load(json_file)["structLogs"]

    last_map = {1: _get_last_map(receipt.receiver, receipt.input[:10])}  # type: ignore
    coverage_eval: Dict = {last_map[1]["address"]: {}}
    maxDepth = 1
    for i in range(len(trace)):
        # if depth has increased, tx has called into a different contract
        if trace[i]["depth"] > trace[i - 1]["depth"]:
            step = trace[i - 1]
            maxDepth += 1
            if step["op"] in ("CREATE", "CREATE2"):
                # creating a new contract
                out = next(x for x in trace[i:] if x["depth"] == step["depth"])
                address = out["stack"][-1][-40:]
                sig = f"<{step['op']}>"
                calldata = None
                # self._new_contracts.append(EthAddress(address))
                # if int(step["stack"][-1], 16):
                #     self._add_internal_xfer(step["address"], address, step["stack"][-1])
            else:
                # calling an existing contract
                stack_idx = -4 if step["op"] in ("CALL", "CALLCODE") else -3
                offset = int(step["stack"][stack_idx], 16)
                length = int(step["stack"][stack_idx - 1], 16)
                calldata = HexBytes("".join(step["memory"]))[offset: offset + length]
                sig = calldata[:4].hex()
                address = step["stack"][-2][-40:]

            depth = trace[i]["depth"]
            last_map[depth] = _get_last_map(EthAddress(address), sig)
            coverage_eval.setdefault(last_map[trace[i]["depth"]]["address"], {})

            if receipt._subcalls == None:
                receipt._subcalls = []
            receipt._subcalls.append(
                {"from": step["address"], "to": EthAddress(address), "op": step["op"]}
            )
            if step["op"] in ("CALL", "CALLCODE"):
                receipt._subcalls[-1]["value"] = int(step["stack"][-3], 16)
            if calldata and last_map[trace[i]["depth"]].get("function"):
                fn = last_map[trace[i]["depth"]]["function"]
                receipt._subcalls[-1]["function"] = fn._input_sig
                try:
                    zip_ = zip(fn.abi["inputs"], fn.decode_input(calldata))
                    inputs = {i[0]["name"]: i[1] for i in zip_}  # type: ignore
                    receipt._subcalls[-1]["inputs"] = inputs
                except Exception:
                    receipt._subcalls[-1]["calldata"] = calldata.hex()
            elif calldata:
                receipt._subcalls[-1]["calldata"] = calldata.hex()

        # update trace from last_map
        last = last_map[trace[i]["depth"]]
        trace[i].update(
            address=last["address"],
            fn=last["internal_calls"][-1],
            jumpDepth=last["jumpDepth"],
            source=False,
        )

        opcode = trace[i]["op"]
        if opcode == "CALL" and int(trace[i]["stack"][-3], 16):
            receipt._add_internal_xfer(
                last["address"], trace[i]["stack"][-2][-40:], trace[i]["stack"][-3]
            )

        if trace[i]["depth"]>= maxDepth and opcode in ("RETURN", "REVERT", "INVALID", "SELFDESTRUCT"):
            subcall: dict = next(
                i for i in receipt._subcalls[::-1] if i["to"] == last["address"]  # type: ignore
            )

            if opcode == "RETURN":
                returndata = _get_memory(trace[i], -1)
                if returndata:
                    fn = last["function"]
                    try:
                        return_values = fn.decode_output(returndata)
                        if len(fn.abi["outputs"]) == 1:
                            return_values = (return_values,)
                        subcall["return_value"] = return_values
                    except Exception:
                        subcall["returndata"] = returndata.hex()
                else:
                    subcall["return_value"] = None
            elif opcode == "SELFDESTRUCT":
                subcall["selfdestruct"] = True
            else:
                if opcode == "REVERT":
                    data = _get_memory(trace[i], -1)
                    if len(data) > 4:
                        try:
                            subcall["revert_msg"] = decode_abi(["string"], data[4:])[0]
                        except Exception:
                            subcall["revert_msg"] = data.hex()

    print(receipt._subcalls)

