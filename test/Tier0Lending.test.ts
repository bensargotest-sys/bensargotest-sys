import { expect } from "chai";
import { ethers } from "hardhat";
import { Tier0Lending, MockERC20 } from "../typechain-types";
import { SignerWithAddress } from "@nomicfoundation/hardhat-ethers/signers";

describe("Tier0Lending", function () {
  let tier0: Tier0Lending;
  let usdc: MockERC20;
  let owner: SignerWithAddress;
  let agent1: SignerWithAddress;
  let agent2: SignerWithAddress;

  const MIN_LOAN = ethers.parseUnits("0.1", 6);
  const MAX_LOAN = ethers.parseUnits("1", 6);
  const LOAN_AMOUNT = ethers.parseUnits("0.5", 6); // $0.50

  beforeEach(async function () {
    [owner, agent1, agent2] = await ethers.getSigners();

    // Deploy mock USDC
    const MockERC20 = await ethers.getContractFactory("MockERC20");
    usdc = await MockERC20.deploy("USD Coin", "USDC", 6);

    // Deploy Tier0Lending
    const Tier0Lending = await ethers.getContractFactory("Tier0Lending");
    tier0 = await Tier0Lending.deploy(await usdc.getAddress());

    // Mint USDC to owner and approve
    await usdc.mint(owner.address, ethers.parseUnits("1000", 6));
    await usdc.approve(await tier0.getAddress(), ethers.parseUnits("1000", 6));

    // Deposit liquidity
    await tier0.depositLiquidity(ethers.parseUnits("100", 6));
  });

  describe("Deployment", function () {
    it("Should set correct min/max loan amounts", async function () {
      expect(await tier0.MIN_LOAN()).to.equal(MIN_LOAN);
      expect(await tier0.MAX_LOAN()).to.equal(MAX_LOAN);
    });

    it("Should set correct loan term (7 days)", async function () {
      const SEVEN_DAYS = 7 * 24 * 60 * 60;
      expect(await tier0.LOAN_TERM()).to.equal(SEVEN_DAYS);
    });

    it("Should set correct interest rate (10%)", async function () {
      expect(await tier0.INTEREST_RATE()).to.equal(1000); // 10% in basis points
    });
  });

  describe("Loan Issuance", function () {
    it("Should issue loan to eligible agent", async function () {
      const eligible = await tier0.isEligible(agent1.address);
      expect(eligible).to.be.true;

      await tier0.connect(agent1).requestLoan(LOAN_AMOUNT);

      const loans = await tier0.getBorrowerLoans(agent1.address);
      expect(loans.length).to.equal(1);

      const loan = await tier0.getLoan(0);
      expect(loan.borrower).to.equal(agent1.address);
      expect(loan.principal).to.equal(LOAN_AMOUNT);
      expect(loan.repaid).to.be.false;
      expect(loan.defaulted).to.be.false;
    });

    it("Should transfer USDC to borrower", async function () {
      await tier0.connect(agent1).requestLoan(LOAN_AMOUNT);
      const balance = await usdc.balanceOf(agent1.address);
      expect(balance).to.equal(LOAN_AMOUNT);
    });

    it("Should update totalDeployed stat", async function () {
      await tier0.connect(agent1).requestLoan(LOAN_AMOUNT);
      const stats = await tier0.getStats();
      expect(stats.deployed).to.equal(LOAN_AMOUNT);
    });

    it("Should reject loan below minimum", async function () {
      const tooSmall = ethers.parseUnits("0.05", 6);
      await expect(
        tier0.connect(agent1).requestLoan(tooSmall)
      ).to.be.revertedWith("Amount out of range");
    });

    it("Should reject loan above maximum", async function () {
      const tooLarge = ethers.parseUnits("2", 6);
      await expect(
        tier0.connect(agent1).requestLoan(tooLarge)
      ).to.be.revertedWith("Amount out of range");
    });

    it("Should reject second loan while first is active", async function () {
      await tier0.connect(agent1).requestLoan(LOAN_AMOUNT);
      await expect(
        tier0.connect(agent1).requestLoan(LOAN_AMOUNT)
      ).to.be.revertedWith("Already has active loan");
    });

    it("Should reject loan from blacklisted borrower", async function () {
      // Issue loan
      await tier0.connect(agent1).requestLoan(LOAN_AMOUNT);

      // Fast forward past due date
      await ethers.provider.send("evm_increaseTime", [7 * 24 * 60 * 60 + 1]);
      await ethers.provider.send("evm_mine", []);

      // Mark default (blacklists borrower)
      await tier0.markDefault(0);

      // Try to request another loan
      await expect(
        tier0.connect(agent1).requestLoan(LOAN_AMOUNT)
      ).to.be.revertedWith("Borrower blacklisted");
    });
  });

  describe("Loan Repayment", function () {
    beforeEach(async function () {
      // Issue loan
      await tier0.connect(agent1).requestLoan(LOAN_AMOUNT);

      // Give agent1 USDC to repay (principal + interest)
      const interest = (LOAN_AMOUNT * 1000n) / 10000n; // 10%
      const totalDue = LOAN_AMOUNT + interest;
      await usdc.mint(agent1.address, totalDue);
      await usdc.connect(agent1).approve(await tier0.getAddress(), totalDue);
    });

    it("Should allow borrower to repay loan", async function () {
      await tier0.connect(agent1).repayLoan(0);

      const loan = await tier0.getLoan(0);
      expect(loan.repaid).to.be.true;
    });

    it("Should update totalRepaid stat", async function () {
      await tier0.connect(agent1).repayLoan(0);
      const stats = await tier0.getStats();
      expect(stats.repaid).to.equal(LOAN_AMOUNT);
    });

    it("Should allow second loan after repaying first", async function () {
      await tier0.connect(agent1).repayLoan(0);

      // Agent should be eligible again
      const eligible = await tier0.isEligible(agent1.address);
      expect(eligible).to.be.true;

      // Request second loan
      await tier0.connect(agent1).requestLoan(LOAN_AMOUNT);
      const loans = await tier0.getBorrowerLoans(agent1.address);
      expect(loans.length).to.equal(2);
    });

    it("Should reject repayment from non-borrower", async function () {
      await expect(
        tier0.connect(agent2).repayLoan(0)
      ).to.be.revertedWith("Not your loan");
    });

    it("Should reject double repayment", async function () {
      await tier0.connect(agent1).repayLoan(0);
      await expect(
        tier0.connect(agent1).repayLoan(0)
      ).to.be.revertedWith("Already repaid");
    });
  });

  describe("Loan Default", function () {
    beforeEach(async function () {
      // Issue loan
      await tier0.connect(agent1).requestLoan(LOAN_AMOUNT);

      // Fast forward past due date
      await ethers.provider.send("evm_increaseTime", [7 * 24 * 60 * 60 + 1]);
      await ethers.provider.send("evm_mine", []);
    });

    it("Should allow anyone to mark loan as defaulted", async function () {
      await tier0.connect(agent2).markDefault(0);

      const loan = await tier0.getLoan(0);
      expect(loan.defaulted).to.be.true;
    });

    it("Should blacklist defaulted borrower", async function () {
      await tier0.markDefault(0);

      const eligible = await tier0.isEligible(agent1.address);
      expect(eligible).to.be.false;

      const blacklisted = await tier0.blacklisted(agent1.address);
      expect(blacklisted).to.be.true;
    });

    it("Should update totalDefaulted stat", async function () {
      await tier0.markDefault(0);

      const stats = await tier0.getStats();
      expect(stats.defaulted).to.equal(LOAN_AMOUNT);
    });

    it("Should calculate default rate correctly", async function () {
      await tier0.markDefault(0);

      const stats = await tier0.getStats();
      // Default rate = (defaulted / deployed) * 10000
      // = (0.5 / 0.5) * 10000 = 10000 (100%)
      expect(stats.defaultRate).to.equal(10000);
    });

    it("Should reject marking default before due date", async function () {
      // Issue new loan
      await tier0.connect(agent2).requestLoan(LOAN_AMOUNT);

      // Try to mark default immediately
      await expect(
        tier0.markDefault(1)
      ).to.be.revertedWith("Not past due date");
    });

    it("Should reject marking already defaulted loan", async function () {
      await tier0.markDefault(0);
      await expect(
        tier0.markDefault(0)
      ).to.be.revertedWith("Already defaulted");
    });
  });

  describe("Statistics", function () {
    it("Should track correct loan count", async function () {
      await tier0.connect(agent1).requestLoan(LOAN_AMOUNT);
      await tier0.connect(agent2).requestLoan(LOAN_AMOUNT);

      const stats = await tier0.getStats();
      expect(stats.loansIssued).to.equal(2);
    });

    it("Should track capital deployed", async function () {
      await tier0.connect(agent1).requestLoan(LOAN_AMOUNT);
      await tier0.connect(agent2).requestLoan(LOAN_AMOUNT);

      const stats = await tier0.getStats();
      expect(stats.deployed).to.equal(LOAN_AMOUNT * 2n);
    });
  });

  describe("Admin Functions", function () {
    it("Should allow owner to deposit liquidity", async function () {
      const amount = ethers.parseUnits("50", 6);
      await tier0.depositLiquidity(amount);

      const balance = await usdc.balanceOf(await tier0.getAddress());
      expect(balance).to.equal(ethers.parseUnits("150", 6));
    });

    it("Should allow owner to withdraw liquidity", async function () {
      const amount = ethers.parseUnits("10", 6);
      await tier0.withdrawLiquidity(amount);

      const balance = await usdc.balanceOf(owner.address);
      expect(balance).to.be.gte(ethers.parseUnits("910", 6));
    });

    it("Should reject withdrawal exceeding balance", async function () {
      const tooMuch = ethers.parseUnits("200", 6);
      await expect(
        tier0.withdrawLiquidity(tooMuch)
      ).to.be.revertedWith("Insufficient balance");
    });

    it("Should reject non-owner admin calls", async function () {
      await expect(
        tier0.connect(agent1).withdrawLiquidity(ethers.parseUnits("10", 6))
      ).to.be.reverted;
    });
  });
});
