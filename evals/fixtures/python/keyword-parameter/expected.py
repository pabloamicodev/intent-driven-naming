def summarize_invoices(id, invoices):
    customer_invoices = [
        invoice for invoice in invoices if invoice["customer_id"] == id
    ]
    return sum(invoice["amount_in_cents"] for invoice in customer_invoices)
