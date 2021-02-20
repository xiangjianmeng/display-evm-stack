pragma solidity >=0.7.0 <0.8.0;

interface Test4 {
    function test4Revert(address tmp) pure external;
}

contract Test3 {

    address public test4;

    constructor(address test) {
        test4 = test;
    }

    function test3Revert(address tmp) public {
        _test3Revert(tmp);
    }

    function _test3Revert(address tmp) public {
        Test4(test4).test4Revert(tmp);
    }
}