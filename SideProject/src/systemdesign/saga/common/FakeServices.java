package systemdesign.saga.common;

import java.util.HashSet;
import java.util.Set;

/**
 * Pretend User, Order, and Payment services.
 * Each method is idempotent: doing it twice with the same orderId is a no-op.
 */
public class FakeServices {

    public final OrderService order = new OrderService();
    public final UserService user = new UserService();
    public final PaymentService payment;

    public FakeServices(boolean paymentFails) {
        this.payment = new PaymentService(paymentFails);
    }

    @Override
    public String toString() {
        return "stockReserved=" + order.reserved
                + ", walletDebited=" + user.debited
                + ", cardCharged=" + payment.charged
                + ", orderStatus=" + order.status;
    }

    public static class OrderService {
        public final Set<String> reserved = new HashSet<>();
        public String status = "NONE";

        public boolean reserveStock(CheckoutRequest req) {
            // already reserved for this order? just say OK
            if (!reserved.add(req.orderId)) {
                System.out.println("  Order: reserve already done for " + req.orderId);
                return true;
            }
            status = "PENDING";
            System.out.println("  Order: reserved " + req.quantity + " x " + req.sku);
            return true;
        }

        public void releaseStock(CheckoutRequest req) {
            if (!reserved.remove(req.orderId)) {
                System.out.println("  Order: release already done for " + req.orderId);
                return;
            }
            status = "CANCELLED";
            System.out.println("  Order: released stock (compensate)");
        }

        public void confirm(CheckoutRequest req) {
            status = "CONFIRMED";
            System.out.println("  Order: confirmed " + req.orderId);
        }
    }

    public static class UserService {
        public final Set<String> debited = new HashSet<>();

        public boolean debitWallet(CheckoutRequest req) {
            if (!debited.add(req.orderId)) {
                System.out.println("  User: debit already done for " + req.orderId);
                return true;
            }
            System.out.println("  User: debited wallet $" + req.amount);
            return true;
        }

        public void creditWallet(CheckoutRequest req) {
            if (!debited.remove(req.orderId)) {
                System.out.println("  User: credit already done for " + req.orderId);
                return;
            }
            System.out.println("  User: credited wallet back (compensate)");
        }
    }

    public static class PaymentService {
        public final Set<String> charged = new HashSet<>();
        private final boolean fail;

        public PaymentService(boolean fail) {
            this.fail = fail;
        }

        public boolean chargeCard(CheckoutRequest req) {
            if (charged.contains(req.orderId)) {
                System.out.println("  Payment: charge already done for " + req.orderId);
                return true;
            }
            if (fail) {
                System.out.println("  Payment: card declined");
                return false;
            }
            charged.add(req.orderId);
            System.out.println("  Payment: charged card $" + req.amount);
            return true;
        }

        public void refundCard(CheckoutRequest req) {
            if (!charged.remove(req.orderId)) {
                System.out.println("  Payment: refund already done for " + req.orderId);
                return;
            }
            System.out.println("  Payment: refunded card (compensate)");
        }
    }
}
