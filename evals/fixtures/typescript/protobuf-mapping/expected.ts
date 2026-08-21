type GeneratedCustomer = { customer_id: string; created_at_ms: number };
type ApplicationCustomer = { customerId: string; createdAtEpochMs: number };

export function mapGeneratedCustomerToApplication(
  generatedCustomer: GeneratedCustomer,
): ApplicationCustomer {
  return {
    customerId: generatedCustomer.customer_id,
    createdAtEpochMs: generatedCustomer.created_at_ms,
  };
}
