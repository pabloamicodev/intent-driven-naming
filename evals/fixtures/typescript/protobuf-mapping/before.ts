type GeneratedCustomer = { customer_id: string; created_at_ms: number };

export function convert(value: GeneratedCustomer) {
  return { id: value.customer_id, created: value.created_at_ms };
}
