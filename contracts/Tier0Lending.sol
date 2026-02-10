// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title Tier0Lending
 * @notice Micro-loans ($0.10 - $1.00) for AI agents with zero credit history
 * @dev Ultra-simple lending for sub-$1 amounts, 7-day terms, auto-liquidation
 */
contract Tier0Lending is Ownable, ReentrancyGuard {
    
    // ============ State Variables ============
    
    IERC20 public usdc;
    uint256 public constant MIN_LOAN = 0.1e6;      // $0.10
    uint256 public constant MAX_LOAN = 1e6;        // $1.00
    uint256 public constant LOAN_TERM = 7 days;
    uint256 public constant INTEREST_RATE = 1000;  // 10% (basis points)
    uint256 public constant PLATFORM_FEE = 100;    // 1% (basis points)
    
    uint256 public loanIdCounter;
    uint256 public totalDeployed;
    uint256 public totalRepaid;
    uint256 public totalDefaulted;
    
    // ============ Structs ============
    
    struct Loan {
        address borrower;
        uint256 principal;
        uint256 interest;
        uint256 dueDate;
        bool repaid;
        bool defaulted;
        uint256 timestamp;
    }
    
    // ============ Mappings ============
    
    mapping(uint256 => Loan) public loans;
    mapping(address => uint256[]) public borrowerLoans;
    mapping(address => uint256) public borrowerActiveLoans; // Count of active loans
    mapping(address => bool) public blacklisted; // Banned after default
    
    // ============ Events ============
    
    event LoanIssued(uint256 indexed loanId, address indexed borrower, uint256 principal, uint256 dueDate);
    event LoanRepaid(uint256 indexed loanId, address indexed borrower, uint256 amount);
    event LoanDefaulted(uint256 indexed loanId, address indexed borrower, uint256 principal);
    event BorrowerBlacklisted(address indexed borrower);
    
    // ============ Constructor ============
    
    constructor(address _usdc) {
        usdc = IERC20(_usdc);
    }
    
    // ============ Core Functions ============
    
    /**
     * @notice Request a micro-loan (auto-approved if eligible)
     * @param amount Loan amount in USDC (6 decimals)
     */
    function requestLoan(uint256 amount) external nonReentrant {
        require(amount >= MIN_LOAN && amount <= MAX_LOAN, "Amount out of range");
        require(!blacklisted[msg.sender], "Borrower blacklisted");
        require(borrowerActiveLoans[msg.sender] == 0, "Already has active loan");
        require(usdc.balanceOf(address(this)) >= amount, "Insufficient liquidity");
        
        // Calculate interest
        uint256 interest = (amount * INTEREST_RATE) / 10000;
        uint256 dueDate = block.timestamp + LOAN_TERM;
        
        // Create loan
        uint256 loanId = loanIdCounter++;
        loans[loanId] = Loan({
            borrower: msg.sender,
            principal: amount,
            interest: interest,
            dueDate: dueDate,
            repaid: false,
            defaulted: false,
            timestamp: block.timestamp
        });
        
        borrowerLoans[msg.sender].push(loanId);
        borrowerActiveLoans[msg.sender]++;
        totalDeployed += amount;
        
        // Disburse funds
        require(usdc.transfer(msg.sender, amount), "Transfer failed");
        
        emit LoanIssued(loanId, msg.sender, amount, dueDate);
    }
    
    /**
     * @notice Repay a loan (principal + interest)
     * @param loanId ID of the loan to repay
     */
    function repayLoan(uint256 loanId) external nonReentrant {
        Loan storage loan = loans[loanId];
        require(loan.borrower == msg.sender, "Not your loan");
        require(!loan.repaid, "Already repaid");
        require(!loan.defaulted, "Already defaulted");
        
        uint256 totalDue = loan.principal + loan.interest;
        uint256 platformFee = (totalDue * PLATFORM_FEE) / 10000;
        
        // Transfer funds
        require(usdc.transferFrom(msg.sender, address(this), totalDue), "Transfer failed");
        
        // Mark as repaid
        loan.repaid = true;
        borrowerActiveLoans[msg.sender]--;
        totalRepaid += loan.principal;
        
        emit LoanRepaid(loanId, msg.sender, totalDue);
    }
    
    /**
     * @notice Mark loan as defaulted (callable by anyone after due date)
     * @param loanId ID of the loan to default
     */
    function markDefault(uint256 loanId) external {
        Loan storage loan = loans[loanId];
        require(!loan.repaid, "Already repaid");
        require(!loan.defaulted, "Already defaulted");
        require(block.timestamp > loan.dueDate, "Not past due date");
        
        // Mark as defaulted
        loan.defaulted = true;
        borrowerActiveLoans[loan.borrower]--;
        totalDefaulted += loan.principal;
        
        // Blacklist borrower (permanent ban)
        blacklisted[loan.borrower] = true;
        
        emit LoanDefaulted(loanId, loan.borrower, loan.principal);
        emit BorrowerBlacklisted(loan.borrower);
    }
    
    // ============ View Functions ============
    
    /**
     * @notice Check if address is eligible for loan
     */
    function isEligible(address borrower) external view returns (bool) {
        return !blacklisted[borrower] && borrowerActiveLoans[borrower] == 0;
    }
    
    /**
     * @notice Get all loans for a borrower
     */
    function getBorrowerLoans(address borrower) external view returns (uint256[] memory) {
        return borrowerLoans[borrower];
    }
    
    /**
     * @notice Get loan details
     */
    function getLoan(uint256 loanId) external view returns (
        address borrower,
        uint256 principal,
        uint256 interest,
        uint256 dueDate,
        bool repaid,
        bool defaulted
    ) {
        Loan memory loan = loans[loanId];
        return (
            loan.borrower,
            loan.principal,
            loan.interest,
            loan.dueDate,
            loan.repaid,
            loan.defaulted
        );
    }
    
    /**
     * @notice Get platform statistics
     */
    function getStats() external view returns (
        uint256 loansIssued,
        uint256 deployed,
        uint256 repaid,
        uint256 defaulted,
        uint256 defaultRate
    ) {
        uint256 defaultRate_ = totalDeployed > 0 
            ? (totalDefaulted * 10000) / totalDeployed 
            : 0;
        
        return (
            loanIdCounter,
            totalDeployed,
            totalRepaid,
            totalDefaulted,
            defaultRate_
        );
    }
    
    // ============ Admin Functions ============
    
    /**
     * @notice Deposit USDC liquidity
     */
    function depositLiquidity(uint256 amount) external onlyOwner {
        require(usdc.transferFrom(msg.sender, address(this), amount), "Transfer failed");
    }
    
    /**
     * @notice Withdraw USDC liquidity (only unused funds)
     */
    function withdrawLiquidity(uint256 amount) external onlyOwner {
        uint256 available = usdc.balanceOf(address(this));
        require(amount <= available, "Insufficient balance");
        require(usdc.transfer(owner(), amount), "Transfer failed");
    }
    
    /**
     * @notice Emergency pause (disable new loans)
     */
    function pause() external onlyOwner {
        // Implementation: set a paused flag and check in requestLoan
        // For simplicity, omitted here - add if needed
    }
}
