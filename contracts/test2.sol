// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.8.0;

contract Test2 {

    function test2Revert() pure external {
        require(false, "call test2Revert");
    }

}