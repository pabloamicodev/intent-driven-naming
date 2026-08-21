const assert = require("node:assert/strict");
const path = require("node:path");

const candidatePath = path.resolve(process.argv[2]);
const { buildSelectionPayload } = require(candidatePath);
const payload = buildSelectionPayload({ id: "customer-42" });

assert.deepEqual(payload, { customerId: "customer-42" });
assert.deepEqual(Object.keys(payload), ["customerId"]);
