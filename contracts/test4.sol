pragma solidity >=0.7.0 <0.8.0;

interface Test5 {
    function test5Revert(address tmp) pure external;
}

contract Test4 {

    address public test5;

    constructor(address test) {
        test5 = test;
    }

    function test4Revert(address tmp) public {
        _test4Revert(tmp);
    }

    function _test4Revert(address tmp) internal {
        Test5(test5).test5Revert(tmp);
    }
}