#[derive(Debug, PartialEq)]
struct Order {
    id: String,
}

struct DraftOrder {
    id: String,
}

impl DraftOrder {
    fn to_order(self) -> Order {
        Order { id: self.id }
    }
}

fn main() {
    let order = DraftOrder { id: "order-7".to_owned() }.to_order();
    assert_eq!(order, Order { id: "order-7".to_owned() });
}
