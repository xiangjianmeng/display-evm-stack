// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.8.0;

interface Test6 {
    function test6Revert() pure external;
}

contract Test5 {

    address public test6;

    constructor(address test) {
        test6 = test;
    }

    function test5Revert() public {
        Test6(test6).test6Revert();
    }
}