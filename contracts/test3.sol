// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.8.0;

interface Test4 {
    function test4Revert() pure external;
}

contract Test3 {

    address public test4;

    constructor(address test) {
        test4 = test;
    }

    function test3Revert() public {
        Test4(test4).test4Revert();
    }
}