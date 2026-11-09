package systemdesign.saga.choreography;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;

import systemdesign.saga.common.CheckoutRequest;
import systemdesign.saga.common.FakeServices.OrderService;
import systemdesign.saga.common.FakeServices.PaymentService;
import systemdesign.saga.common.FakeServices.UserService;

/**
 * Choreography SAGA.
 *
 * There is no boss class that calls services in a loop.
 * Each service listens for an event, does its local step, then publishes the next event.
 * On failure it publishes a "failed" event, and earlier services undo themselves.
 *
 * Happy path events:
 *   CheckoutStarted -> StockReserved -> WalletDebited -> CardCharged -> OrderConfirmed
 *
 * Failure path (card declined):
 *   CardChargeFailed -> WalletCredited -> StockReleased -> OrderCancelled
 *
 * The Bus below is a toy in-memory event bus so you can run this without Kafka/RabbitMQ.
 */
public class CheckoutChoreography {

    private final Bus bus = new Bus();
    private final OrderService order;
    private final UserService user;
    private final PaymentService payment;
    private boolean confirmed;

    public CheckoutChoreography(OrderService order, UserService user, PaymentService payment) {
        this.order = order;
        this.user = user;
        this.payment = payment;
        wireListeners();
    }

    /** @return true if the order is confirmed */
    public boolean checkout(CheckoutRequest req) {
        confirmed = false;
        System.out.println("Choreography starts " + req.orderId);
        bus.publish("CheckoutStarted", req);
        return confirmed;
    }

    private void wireListeners() {
        // --- forward path: each service reacts, then publishes the next event ---

        bus.on("CheckoutStarted", req -> {
            if (order.reserveStock(req)) {
                bus.publish("StockReserved", req);
            } else {
                bus.publish("OrderCancelled", req);
            }
        });

        bus.on("StockReserved", req -> {
            if (user.debitWallet(req)) {
                bus.publish("WalletDebited", req);
            } else {
                bus.publish("WalletDebitFailed", req);
            }
        });

        bus.on("WalletDebited", req -> {
            if (payment.chargeCard(req)) {
                bus.publish("CardCharged", req);
            } else {
                bus.publish("CardChargeFailed", req);
            }
        });

        bus.on("CardCharged", req -> {
            order.confirm(req);
            confirmed = true;
            bus.publish("OrderConfirmed", req);
        });

        // --- compensate path: undo in reverse, one event at a time ---

        bus.on("CardChargeFailed", req -> {
            user.creditWallet(req);
            bus.publish("WalletCredited", req);
        });

        bus.on("WalletDebitFailed", req -> bus.publish("WalletCredited", req));

        bus.on("WalletCredited", req -> {
            order.releaseStock(req);
            bus.publish("StockReleased", req);
        });

        bus.on("StockReleased", req -> {
            order.status = "CANCELLED";
            bus.publish("OrderCancelled", req);
        });
    }

    /** Tiny pub/sub. Listeners run immediately, in the order they were registered. */
    static class Bus {
        private final Map<String, List<Consumer<CheckoutRequest>>> listeners = new HashMap<>();

        void on(String event, Consumer<CheckoutRequest> listener) {
            listeners.computeIfAbsent(event, key -> new ArrayList<>()).add(listener);
        }

        void publish(String event, CheckoutRequest req) {
            System.out.println("  event: " + event);
            for (Consumer<CheckoutRequest> listener : listeners.getOrDefault(event, List.of())) {
                listener.accept(req);
            }
        }
    }
}
