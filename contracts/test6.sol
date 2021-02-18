// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.8.0;

contract Test6 {

    function test6Revert() pure external {
        require(false, "call test6Revert");
    }

}