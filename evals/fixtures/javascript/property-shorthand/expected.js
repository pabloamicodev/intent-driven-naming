function buildSelectionPayload(customer) {
  const selectedCustomerId = customer.id;
  return { customerId: selectedCustomerId };
}

module.exports = { buildSelectionPayload };
