## 1. Generate transaction trace

### 1.1 Run okexchain local

```
cd okexchain
git checkout mxj/evm-debug
./tools/initevm_web3_rest.sh
```

### 1.2 Deploy test contract

1. Deploy `./contracts/test2.sol` 

2. Deploy `./contracts/test1.sol` with test2’s address

3. Call test1’s test1Revert and get the `txhash`

4. Find trace file in `./tools/_cache_evm/traces` according to the `txhash` and copy it to `./traces` of current repository

5. Down load the repository

   ```
   git clone https://github.com/xiangjianmeng/display-evm-stack.git
   cd dispay-evm-stack
   mkdir traces
   cp ${path}/okexchain/tools/_cache_evm/traces/${txhash} ./traces
   ```

6. Copy abi of test2.sol from remix to `./build/contracts/test2.abi` and the same to test1.sol

   ![image-20210218113915368](./img/image-20210218113915368.png)

## 2. Display the transaction call stack

### 2.1 Edit the `__main__.py`

```python
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
```

1. change the `txhash` to the hash of tx to display the call stack.
2. Register the contract to `addr_to_contract`, key is the address of contract, value is the Contract instance. If thers is no corresponding abi of a contract, ignore the arg. It will only display the signature of the function without function name.

### 2.2 Run `__main__.py`

```
$ python3 __main__.py                                                                                                                                                                            
[{'from': '0xd84d4030880352B03F6746ACa893a4aF9EDC6134', 'to': '0x1d29789a81aa381fE5830cd378Bb8F5c76E8C8a7', 'op': 'STATICCALL', 'function': 'test2Revert()', 'inputs': {}, 'revert_msg': 'call test2Revert'}]
```











