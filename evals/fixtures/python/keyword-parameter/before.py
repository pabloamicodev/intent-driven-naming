def summarize_invoices(id, invoices):
    data = [invoice for invoice in invoices if invoice["customer_id"] == id]
    return sum(invoice["amount_in_cents"] for invoice in data)
