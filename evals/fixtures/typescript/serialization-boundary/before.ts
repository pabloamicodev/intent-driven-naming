export interface InvoiceWire {
  amount_in_cents: number;
}

export function calc(data: InvoiceWire[]): number {
  return data.reduce((value, item) => value + item.amount_in_cents, 0);
}
