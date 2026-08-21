export interface InvoiceWire {
  amount_in_cents: number;
}

export function totalInvoiceCents(invoices: InvoiceWire[]): number {
  return invoices.reduce(
    (totalCents, invoice) => totalCents + invoice.amount_in_cents,
    0,
  );
}
