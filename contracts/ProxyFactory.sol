// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./TokenProxy.sol";

contract ProxyFactory {
    address public immutable REAL_USDT = 0xa614f803B6FD780986A42c78Ec9c7f77e6DeD13C;
    address public implementation;

    event ProxyCreated(address proxy);

    constructor(address _implementation) {
        implementation = _implementation;
    }

    function createProxy(bytes32 salt) external returns (address) {
        bytes memory bytecode = abi.encodePacked(
            type(TokenProxy).creationCode,
            abi.encode(implementation)
        );
        address proxy;
        assembly {
            proxy := create2(0, add(bytecode, 0x20), mload(bytecode), salt)
        }
        require(proxy != address(0), "Proxy creation failed");
        emit ProxyCreated(proxy);
        return proxy;
    }
}