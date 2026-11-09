package systemdesign.saga.orchestration;

import systemdesign.saga.common.CheckoutRequest;
import systemdesign.saga.common.FakeServices.OrderService;
import systemdesign.saga.common.FakeServices.PaymentService;
import systemdesign.saga.common.FakeServices.UserService;

/**
 * Orchestration SAGA.
 *
 * One class owns the whole checkout story. It calls each service in order.
 * If a step fails, it runs the undo (compensate) steps in reverse.
 *
 * Steps:
 *   1. Order.reserveStock     undo: Order.releaseStock
 *   2. User.debitWallet       undo: User.creditWallet
 *   3. Payment.chargeCard     undo: Payment.refundCard
 *   4. Order.confirm
 */
public class CheckoutSagaOrchestrator {

    private final OrderService order;
    private final UserService user;
    private final PaymentService payment;

    public CheckoutSagaOrchestrator(OrderService order, UserService user, PaymentService payment) {
        this.order = order;
        this.user = user;
        this.payment = payment;
    }

    /** @return true if the order is confirmed */
    public boolean checkout(CheckoutRequest req) {
        System.out.println("Orchestrator starts " + req.orderId);

        if (!order.reserveStock(req)) {
            return false; // nothing to undo yet
        }

        if (!user.debitWallet(req)) {
            order.releaseStock(req);
            return false;
        }

        if (!payment.chargeCard(req)) {
            // payment failed — undo the steps that already succeeded, newest first
            user.creditWallet(req);
            order.releaseStock(req);
            return false;
        }

        order.confirm(req);
        return true;
    }
}
