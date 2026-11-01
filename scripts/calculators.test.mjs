import assert from "node:assert/strict";
import test from "node:test";
import { calculateFire, calculateTravel } from "../assets/calculations.js";

test("FIRE target is annual spending divided by the selected withdrawal rate", () => {
  const result = calculateFire({ assets: 0, monthlySaving: 10000, monthlySpending: 20000, nominalReturn: 5, inflation: 2, withdrawalRate: 4 });
  assert.equal(result.target, 6000000);
  assert.ok(result.years > 0);
  assert.equal(result.reached, true);
});

test("real return accounts for inflation", () => {
  const result = calculateFire({ assets: 0, monthlySaving: 10000, monthlySpending: 20000, nominalReturn: 5, inflation: 2, withdrawalRate: 4 });
  assert.ok(Math.abs(result.realReturn - 0.02941176470588236) < 1e-12);
});

test("travel budget separates trip cost, reserve, funding, and gap", () => {
  const result = calculateTravel({ months: 3, monthlyTravel: 18000, monthlyHome: 8000, oneOff: 12000, buffer: 30000, available: 100000, monthlyIncome: 0 });
  assert.equal(result.tripCosts, 90000);
  assert.equal(result.totalNeed, 120000);
  assert.equal(result.gap, 20000);
});

test("invalid calculator inputs are rejected", () => {
  assert.throws(() => calculateFire({ assets: -1, monthlySaving: 0, monthlySpending: 1, nominalReturn: 5, inflation: 2, withdrawalRate: 4 }), /檢查數值範圍/);
  assert.throws(() => calculateTravel({ months: 0, monthlyTravel: 1, monthlyHome: 0, oneOff: 0, buffer: 0, available: 0, monthlyIncome: 0 }), /檢查數值範圍/);
});
