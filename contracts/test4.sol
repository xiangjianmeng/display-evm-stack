// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.8.0;

interface Test5 {
    function test5Revert() pure external;
}

contract Test4 {

    address public test5;

    constructor(address test) {
        test5 = test;
    }

    function test4Revert() public {
        Test5(test5).test5Revert();
    }
}