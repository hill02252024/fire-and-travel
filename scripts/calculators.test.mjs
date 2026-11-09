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

test("calculator page forms render results after submission", async () => {
  const fireForm = { values: { currency: "HKD", assets: "1000000", monthlySaving: "10000", monthlySpending: "20000", nominalReturn: "5", inflation: "2", withdrawalRate: "4" } };
  const travelForm = { values: { currency: "HKD", months: "3", monthlyTravel: "18000", monthlyHome: "8000", oneOff: "15000", buffer: "30000", available: "90000", monthlyIncome: "10000" } };
  const fireResult = { innerHTML: "" };
  const travelResult = { innerHTML: "" };
  const listeners = new Map();
  const originalDocument = globalThis.document;
  const originalFormData = globalThis.FormData;
  class FormDataMock {
    constructor(form) {
      this.entries = Object.entries(form.values);
    }
    [Symbol.iterator]() {
      return this.entries[Symbol.iterator]();
    }
  }
  globalThis.document = {
    querySelector(selector) {
      if (selector === "#fire-form") return { addEventListener: (type, listener) => listeners.set(selector, listener), values: fireForm.values };
      if (selector === "#travel-form") return { addEventListener: (type, listener) => listeners.set(selector, listener), values: travelForm.values };
      if (selector === "#fire-result") return fireResult;
      if (selector === "#travel-result") return travelResult;
      return null;
    }
  };
  globalThis.FormData = FormDataMock;
  try {
    await import(`../assets/site.js?test=${Date.now()}`);
    listeners.get("#fire-form")({ preventDefault() {} });
    listeners.get("#travel-form")({ preventDefault() {} });
    assert.match(fireResult.innerHTML, /6,000,000/);
    assert.match(fireResult.innerHTML, /估算所需時間/);
    assert.match(travelResult.innerHTML, /123,000/);
    assert.match(travelResult.innerHTML, /仍需預備/);
  } finally {
    if (originalDocument === undefined) delete globalThis.document;
    else globalThis.document = originalDocument;
    if (originalFormData === undefined) delete globalThis.FormData;
    else globalThis.FormData = originalFormData;
  }
});
