// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.8.0;


interface Test2 {
    function test2Revert() pure external;
}

contract Test1 {

    address public test2;

    constructor(address test) {
        test2 = test;
    }

    function test1Revert() public {
        Test2(test2).test2Revert();
    }
}