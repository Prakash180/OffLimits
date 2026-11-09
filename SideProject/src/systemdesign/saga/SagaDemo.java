package systemdesign.saga;

import systemdesign.saga.choreography.CheckoutChoreography;
import systemdesign.saga.common.CheckoutRequest;
import systemdesign.saga.common.FakeServices;
import systemdesign.saga.orchestration.CheckoutSagaOrchestrator;

/**
 * Tiny demo of both SAGA styles for a checkout:
 *   1. Reserve stock   (Order)
 *   2. Debit wallet    (User)
 *   3. Charge card     (Payment)
 *
 * If a later step fails, earlier steps are undone (compensated).
 * Run this class's main method.
 */
public class SagaDemo {

    public static void main(String[] args) {
        System.out.println("========== ORCHESTRATION (happy path) ==========");
        runOrchestration(false);

        System.out.println("\n========== ORCHESTRATION (payment fails) ==========");
        runOrchestration(true);

        System.out.println("\n========== CHOREOGRAPHY (happy path) ==========");
        runChoreography(false);

        System.out.println("\n========== CHOREOGRAPHY (payment fails) ==========");
        runChoreography(true);
    }

    private static void runOrchestration(boolean paymentFails) {
        FakeServices services = new FakeServices(paymentFails);
        CheckoutSagaOrchestrator saga = new CheckoutSagaOrchestrator(
                services.order, services.user, services.payment);

        boolean ok = saga.checkout(new CheckoutRequest("order-1", "user-1", "SKU-9", 2, 50));
        System.out.println("result = " + (ok ? "CONFIRMED" : "CANCELLED"));
        System.out.println(services);
    }

    private static void runChoreography(boolean paymentFails) {
        FakeServices services = new FakeServices(paymentFails);
        CheckoutChoreography saga = new CheckoutChoreography(
                services.order, services.user, services.payment);

        boolean ok = saga.checkout(new CheckoutRequest("order-1", "user-1", "SKU-9", 2, 50));
        System.out.println("result = " + (ok ? "CONFIRMED" : "CANCELLED"));
        System.out.println(services);
    }
}
