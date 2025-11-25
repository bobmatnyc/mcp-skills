---
name: Web3 & Blockchain Development
skill_id: web3-blockchain
version: 1.0.0
description: Production-grade Web3 development with Solidity smart contracts, ethers.js/web3.js integration, DApp architecture, security patterns, and AI-enhanced blockchain development (ChatWeb3, Aider + Gemini 2024)
category: Blockchain & Web3
tags:
  - web3
  - blockchain
  - solidity
  - ethereum
  - smart-contracts
  - dapp
  - ethers
  - hardhat
  - security
  - defi
author: mcp-skillset
license: MIT
created: 2025-11-25
last_updated: 2025-11-25
toolchain:
  - Solidity 0.8+
  - Hardhat
  - ethers.js v6
  - OpenZeppelin Contracts
frameworks:
  - Ethereum
  - Hardhat
  - Foundry
  - OpenZeppelin
related_skills:
  - security-testing
  - test-driven-development
  - fastapi-web-development
  - cloudflare-edge-ai
---

# Web3 & Blockchain Development

## Overview

Master Web3 development with Solidity smart contracts, DApp architecture, and modern tooling (Hardhat, ethers.js v6). Learn security-first patterns, gas optimization, and AI-enhanced development with ChatWeb3 and Aider + Gemini for Solidity (2024).

## When to Use This Skill

- Building decentralized applications (DApps) on Ethereum
- Writing secure smart contracts for DeFi, NFTs, or DAOs
- Creating token contracts (ERC-20, ERC-721, ERC-1155)
- Integrating blockchain functionality into web applications
- Auditing smart contracts for security vulnerabilities
- Optimizing gas costs for efficient contract execution
- Deploying contracts to mainnet or Layer 2 networks

## Core Principles

### 1. Solidity Security Patterns

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

// ✅ GOOD: Security-first contract
contract SecureWallet is ReentrancyGuard, Ownable, Pausable {
    mapping(address => uint256) public balances;

    event Deposit(address indexed user, uint256 amount);
    event Withdrawal(address indexed user, uint256 amount);

    // ✅ Use receive() for accepting Ether
    receive() external payable {
        balances[msg.sender] += msg.value;
        emit Deposit(msg.sender, msg.value);
    }

    // ✅ Checks-Effects-Interactions pattern (prevents reentrancy)
    function withdraw(uint256 amount) external nonReentrant whenNotPaused {
        // Checks
        require(amount > 0, "Amount must be greater than 0");
        require(balances[msg.sender] >= amount, "Insufficient balance");

        // Effects (update state BEFORE external call)
        balances[msg.sender] -= amount;

        // Interactions (external call last)
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");

        emit Withdrawal(msg.sender, amount);
    }

    // ✅ Emergency stop mechanism
    function pause() external onlyOwner {
        _pause();
    }

    function unpause() external onlyOwner {
        _unpause();
    }
}

// ❌ BAD: Vulnerable to reentrancy attack
contract VulnerableWallet {
    mapping(address => uint256) public balances;

    function withdraw(uint256 amount) external {
        require(balances[msg.sender] >= amount);

        // ❌ WRONG: External call before state update
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success);

        // Attacker can re-enter withdraw() before this line executes!
        balances[msg.sender] -= amount;
    }
}
```

**Common Vulnerabilities (SWC Registry)**:
1. Reentrancy (SWC-107) - Use ReentrancyGuard
2. Integer Overflow/Underflow (SWC-101) - Solidity 0.8+ has built-in checks
3. Unchecked Call Return Values (SWC-104) - Always check success
4. Unprotected Ether Withdrawal (SWC-105) - Use access control
5. Delegatecall to Untrusted Callee (SWC-112) - Avoid or whitelist
6. Timestamp Dependence (SWC-116) - Don't rely on block.timestamp for randomness

### 2. ERC Token Standards

```solidity
// ERC-20 Token (Fungible Token)
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract MyToken is ERC20, Ownable {
    constructor() ERC20("MyToken", "MTK") {
        _mint(msg.sender, 1000000 * 10 ** decimals());
    }

    // Optional: Mint new tokens
    function mint(address to, uint256 amount) external onlyOwner {
        _mint(to, amount);
    }
}

// ERC-721 NFT (Non-Fungible Token)
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";

contract MyNFT is ERC721, ERC721URIStorage, Ownable {
    uint256 private _tokenIdCounter;

    constructor() ERC721("MyNFT", "MNFT") {}

    function safeMint(address to, string memory uri) external onlyOwner {
        uint256 tokenId = _tokenIdCounter++;
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, uri);
    }

    // Override required by Solidity
    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        return super.tokenURI(tokenId);
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}

// ERC-1155 (Multi-Token Standard)
import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";

contract GameItems is ERC1155, Ownable {
    uint256 public constant GOLD = 0;
    uint256 public constant SILVER = 1;
    uint256 public constant SWORD = 2;

    constructor() ERC1155("https://game.example/api/item/{id}.json") {
        _mint(msg.sender, GOLD, 10**18, "");
        _mint(msg.sender, SILVER, 10**27, "");
        _mint(msg.sender, SWORD, 1, "");
    }

    function mint(address account, uint256 id, uint256 amount)
        external
        onlyOwner
    {
        _mint(account, id, amount, "");
    }
}
```

### 3. Gas Optimization Techniques

```solidity
// ❌ BAD: Expensive storage operations
contract Expensive {
    uint256[] public numbers;

    function addNumbers(uint256[] memory nums) external {
        for (uint256 i = 0; i < nums.length; i++) {
            numbers.push(nums[i]);  // SSTORE every iteration (expensive!)
        }
    }
}

// ✅ GOOD: Batch operations and minimize SSTORE
contract Optimized {
    uint256[] public numbers;

    function addNumbers(uint256[] memory nums) external {
        uint256 length = nums.length;  // Cache array length
        for (uint256 i; i < length; ) {  // Skip initialization (i = 0)
            numbers.push(nums[i]);
            unchecked { ++i; }  // Skip overflow check (safe here)
        }
    }
}

// ✅ Use uint256 (native word size) instead of smaller types
uint256 a;  // Cheaper than uint8, uint16, etc.

// ✅ Pack storage variables
struct User {
    address wallet;      // 20 bytes
    uint96 balance;      // 12 bytes (fits in same slot)
    uint32 lastUpdate;   // 4 bytes (fits in same slot)
    bool isActive;       // 1 byte (fits in same slot)
}  // Total: 1 storage slot (32 bytes) instead of 4 slots!

// ✅ Use events instead of storage for historical data
event Transfer(address indexed from, address indexed to, uint256 amount);

// ✅ Use immutable and constant
address public immutable OWNER;  // Set in constructor, cheaper than storage
uint256 public constant MAX_SUPPLY = 1000000;  // Compile-time constant

// ✅ Short-circuit evaluations
require(msg.sender == owner || balances[msg.sender] > 0);  // Cheap check first

// ✅ Use calldata for read-only function parameters
function process(uint256[] calldata data) external {
    // calldata is cheaper than memory for external functions
}
```

**Gas Cost Reference**:
- SLOAD (read storage): 2,100 gas
- SSTORE (write storage): 20,000 gas (first time), 5,000 gas (subsequent)
- CALL (external call): 2,600 gas
- Memory operations: 3 gas per 32 bytes

### 4. DApp Frontend Integration (ethers.js v6)

```typescript
import { ethers } from 'ethers';

// Connect to MetaMask
const provider = new ethers.BrowserProvider(window.ethereum);
await provider.send("eth_requestAccounts", []);
const signer = await provider.getSigner();

// Contract ABI and address
const contractAddress = "0x...";
const abi = [
  "function balanceOf(address owner) view returns (uint256)",
  "function transfer(address to, uint256 amount) returns (bool)",
  "event Transfer(address indexed from, address indexed to, uint256 amount)"
];

// Create contract instance
const contract = new ethers.Contract(contractAddress, abi, signer);

// Read from contract (free, no transaction)
const balance = await contract.balanceOf(signer.address);
console.log(`Balance: ${ethers.formatEther(balance)} ETH`);

// Write to contract (requires transaction & gas)
const tx = await contract.transfer(
  "0xRecipientAddress",
  ethers.parseEther("1.0")
);

// Wait for confirmation
const receipt = await tx.wait();
console.log(`Transaction confirmed in block ${receipt.blockNumber}`);

// Listen to events
contract.on("Transfer", (from, to, amount, event) => {
  console.log(`Transfer: ${from} -> ${to}: ${ethers.formatEther(amount)} ETH`);
});

// Type-safe contract with TypeChain
import { MyToken__factory } from './typechain-types';
const typedContract = MyToken__factory.connect(contractAddress, signer);
```

### 5. Testing with Hardhat

```typescript
// test/MyToken.test.ts
import { expect } from "chai";
import { ethers } from "hardhat";
import { MyToken } from "../typechain-types";

describe("MyToken", function () {
  let token: MyToken;
  let owner: any;
  let addr1: any;

  beforeEach(async function () {
    [owner, addr1] = await ethers.getSigners();

    const TokenFactory = await ethers.getContractFactory("MyToken");
    token = await TokenFactory.deploy();
    await token.waitForDeployment();
  });

  it("Should assign total supply to owner", async function () {
    const ownerBalance = await token.balanceOf(owner.address);
    expect(await token.totalSupply()).to.equal(ownerBalance);
  });

  it("Should transfer tokens between accounts", async function () {
    const amount = ethers.parseEther("50");

    await token.transfer(addr1.address, amount);
    expect(await token.balanceOf(addr1.address)).to.equal(amount);
  });

  it("Should fail if sender doesn't have enough tokens", async function () {
    const amount = ethers.parseEther("1000000");

    await expect(
      token.connect(addr1).transfer(owner.address, amount)
    ).to.be.revertedWith("ERC20: transfer amount exceeds balance");
  });

  it("Should emit Transfer event", async function () {
    const amount = ethers.parseEther("50");

    await expect(token.transfer(addr1.address, amount))
      .to.emit(token, "Transfer")
      .withArgs(owner.address, addr1.address, amount);
  });
});

// Run tests:
// npx hardhat test
// npx hardhat coverage  (with solidity-coverage plugin)
```

## Best Practices

### Project Structure (Hardhat)
```
blockchain-project/
├── contracts/
│   ├── MyToken.sol
│   ├── MyNFT.sol
│   └── interfaces/
│       └── IMyToken.sol
├── test/
│   ├── MyToken.test.ts
│   └── MyNFT.test.ts
├── scripts/
│   ├── deploy.ts
│   └── verify.ts
├── hardhat.config.ts
├── .env
├── .gitignore
└── package.json
```

### Deployment Script
```typescript
// scripts/deploy.ts
import { ethers } from "hardhat";

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Deploying contracts with:", deployer.address);

  const balance = await ethers.provider.getBalance(deployer.address);
  console.log("Account balance:", ethers.formatEther(balance));

  const TokenFactory = await ethers.getContractFactory("MyToken");
  const token = await TokenFactory.deploy();
  await token.waitForDeployment();

  console.log("Token deployed to:", await token.getAddress());

  // Wait for block confirmations before verification
  if (process.env.ETHERSCAN_API_KEY) {
    console.log("Waiting for block confirmations...");
    await token.deploymentTransaction()?.wait(6);

    console.log("Verifying contract on Etherscan...");
    await run("verify:verify", {
      address: await token.getAddress(),
      constructorArguments: [],
    });
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});

// Deploy: npx hardhat run scripts/deploy.ts --network sepolia
```

### Hardhat Configuration
```typescript
// hardhat.config.ts
import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";
import "dotenv/config";

const config: HardhatUserConfig = {
  solidity: {
    version: "0.8.20",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200,  // Balance between deployment cost and execution cost
      },
    },
  },
  networks: {
    hardhat: {
      chainId: 31337,
    },
    sepolia: {
      url: process.env.SEPOLIA_RPC_URL || "",
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
    },
    mainnet: {
      url: process.env.MAINNET_RPC_URL || "",
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
    },
  },
  etherscan: {
    apiKey: process.env.ETHERSCAN_API_KEY,
  },
  gasReporter: {
    enabled: process.env.REPORT_GAS === "true",
    currency: "USD",
    coinmarketcap: process.env.COINMARKETCAP_API_KEY,
  },
};

export default config;
```

## Common Patterns

### Upgradeable Contracts (Proxy Pattern)
```solidity
// Using OpenZeppelin Upgradeable
import "@openzeppelin/contracts-upgradeable/token/ERC20/ERC20Upgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";

contract MyTokenV1 is Initializable, ERC20Upgradeable {
    function initialize() public initializer {
        __ERC20_init("MyToken", "MTK");
        _mint(msg.sender, 1000000 * 10 ** decimals());
    }

    // No constructor! Use initialize() instead
}

// Deploy with hardhat-upgrades plugin
import { ethers, upgrades } from "hardhat";

const TokenV1 = await ethers.getContractFactory("MyTokenV1");
const proxy = await upgrades.deployProxy(TokenV1, [], { initializer: 'initialize' });
```

### Oracle Integration (Chainlink)
```solidity
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract PriceConsumer {
    AggregatorV3Interface internal priceFeed;

    constructor() {
        // ETH/USD on Sepolia
        priceFeed = AggregatorV3Interface(
            0x694AA1769357215DE4FAC081bf1f309aDC325306
        );
    }

    function getLatestPrice() public view returns (int) {
        (, int price, , , ) = priceFeed.latestRoundData();
        return price;
    }
}
```

## Security Auditing Tools

```bash
# Slither (static analysis)
pip3 install slither-analyzer
slither ./contracts

# Mythril (symbolic execution)
pip3 install mythril
myth analyze contracts/MyToken.sol

# Echidna (fuzzing)
docker run -v $(pwd):/code trailofbits/echidna /code/contracts/MyToken.sol

# Foundry (property testing)
forge install
forge test --match-test invariant

# Manual audit checklist:
# 1. Access control on sensitive functions
# 2. Reentrancy guards on external calls
# 3. Integer overflow/underflow checks
# 4. Proper use of tx.origin vs msg.sender
# 5. Gas optimization opportunities
# 6. Event emission for state changes
```

## AI-Enhanced Web3 Development (2024)

```
ChatWeb3 (conversational Solidity assistant):
- Natural language to Solidity code generation
- Security pattern recommendations
- Gas optimization suggestions

Aider + Google Gemini for Solidity:
- Context-aware code completion
- Vulnerability detection during development
- Refactoring assistance

Usage: "Write a secure ERC-20 token with vesting schedule"
→ Generates OpenZeppelin-based contract with best practices
```

## Anti-Patterns

### ❌ DON'T: Use tx.origin for authentication
```solidity
// BAD: Vulnerable to phishing attacks
function withdraw() external {
    require(tx.origin == owner);  // ❌ NEVER!
    // ...
}

// GOOD: Use msg.sender
function withdraw() external {
    require(msg.sender == owner);  // ✅
    // ...
}
```

### ❌ DON'T: Use block.timestamp for randomness
```solidity
// BAD: Miners can manipulate
uint256 random = uint256(keccak256(abi.encodePacked(block.timestamp)));

// GOOD: Use Chainlink VRF for secure randomness
```

### ❌ DON'T: Ignore return values
```solidity
// BAD: Unchecked external call
address(target).call(data);

// GOOD: Check success
(bool success, ) = address(target).call(data);
require(success, "Call failed");
```

## Related Skills

- **security-testing**: Audit smart contracts for vulnerabilities
- **test-driven-development**: Write tests before contract implementation
- **fastapi-web-development**: Build Web3 backend APIs
- **cloudflare-edge-ai**: Deploy Web3 frontends at the edge

## Additional Resources

- Solidity Documentation: https://docs.soliditylang.org
- OpenZeppelin Contracts: https://docs.openzeppelin.com/contracts
- Hardhat: https://hardhat.org/docs
- ethers.js v6: https://docs.ethers.org/v6
- Smart Contract Weakness Classification: https://swcregistry.io
- Consensys Best Practices: https://consensys.github.io/smart-contract-best-practices

## Example Questions

- "Write a secure ERC-20 token contract with minting"
- "How do I prevent reentrancy attacks?"
- "Show me how to optimize gas costs in this contract"
- "Integrate Chainlink price feed into my DeFi contract"
- "Write tests for this NFT contract with Hardhat"
- "Deploy this contract to Sepolia testnet"
- "Audit this contract for security vulnerabilities"
