def build_checkout_attempt_metric(result_label_value, payment_method_label_value):
    metric_name = "checkout_attempts_total"
    metric_labels = {
        "result": result_label_value,
        "payment_method": payment_method_label_value,
    }
    increment_amount = 1
    return metric_name, metric_labels, increment_amount
