package systemdesign.saga.common;

/** One checkout. orderId is the idempotency key — same id must not be applied twice. */
public class CheckoutRequest {
    public final String orderId;
    public final String userId;
    public final String sku;
    public final int quantity;
    public final int amount;

    public CheckoutRequest(String orderId, String userId, String sku, int quantity, int amount) {
        this.orderId = orderId;
        this.userId = userId;
        this.sku = sku;
        this.quantity = quantity;
        this.amount = amount;
    }
}
