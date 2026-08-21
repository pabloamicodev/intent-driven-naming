interface CustomerSource {
    String get(String id);
}

public class Implementation implements CustomerSource {
    @Override
    public String get(String id) {
        return normalizeCustomerId(id);
    }

    private String normalizeCustomerId(String id) {
        return id.trim().toLowerCase();
    }

    public static void main(String[] args) {
        CustomerSource source = new Implementation();
        if (!"customer-9".equals(source.get(" CUSTOMER-9 "))) {
            throw new AssertionError("unexpected customer identifier");
        }
    }
}
