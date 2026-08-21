function buildSelectionPayload(customer) {
  const customerId = customer.id;
  return { customerId };
}

module.exports = { buildSelectionPayload };
