pragma solidity >=0.7.0 <0.8.0;

interface Test6 {
    function test6Revert(address tmp) pure external;
}

contract Test5 {

    address public test6;

    constructor(address test) {
        test6 = test;
    }

    function test5Revert(address tmp) public {
        _test5Revert(tmp);
    }

    function _test5Revert(address tmp) internal {
        Test6(test6).test6Revert(tmp);
    }
}