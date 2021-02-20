// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.8.0;

interface Test3 {
    function test3Revert(address tmp) pure external;
}

contract Test2 {

    address public test3;

    constructor(address test) {
        test3 = test;
    }

    function test2Revert(address tmp) public {
        _test2Revert(tmp);
    }

    function _test2Revert(address tmp) internal {
        Test3(test3).test3Revert(tmp);
    }
}