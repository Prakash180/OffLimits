package systemdesign.messagequeue;

import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Demonstrates at-least-once delivery + why consumers must be idempotent:
 * - 5 "orders" are sent to the queue.
 * - The consumer deliberately "crashes" (never acks) the first time it sees
 *   order-1, so the queue redelivers it after the visibility timeout.
 * - An idempotent guard (a set of already-processed ids) makes sure the
 *   redelivered duplicate isn't charged/processed twice.
 */
public class MessageQueueDemo {

    public static void run() throws InterruptedException {
        InMemoryMessageQueue queue = new InMemoryMessageQueue(300); // 300ms visibility timeout

        int totalOrders = 5;
        for (int i = 1; i <= totalOrders; i++) {
            queue.send(new Message("order-" + i, "payload-for-order-" + i));
        }

        Set<String> processedIds = ConcurrentHashMap.newKeySet();
        AtomicInteger receiveCalls = new AtomicInteger();
        AtomicInteger duplicateDeliveries = new AtomicInteger();
        boolean simulatedCrashDone = false;

        // Keep pulling until every unique order has been processed once.
        while (processedIds.size() < totalOrders) {
            Message message = queue.receive(500);
            if (message == null) {
                continue; // nothing available right now, keep polling
            }
            receiveCalls.incrementAndGet();

            // Simulate a consumer crash on the very first delivery of order-1:
            // it receives the message but never acks it, so the queue must redeliver it later.
            if (!simulatedCrashDone && message.getId().equals("order-1")) {
                simulatedCrashDone = true;
                System.out.println("Consumer received " + message.getId()
                        + " but CRASHED before acking (simulated) — expect redelivery.");
                continue; // no ack -> visibility timeout will expire -> redelivered
            }

            if (!processedIds.add(message.getId())) {
                duplicateDeliveries.incrementAndGet();
                System.out.println("Duplicate delivery of " + message.getId()
                        + " — already processed, skipping (idempotent consumer).");
                queue.ack(message.getId());
                continue;
            }

            System.out.println("Processed " + message.getId() + " (" + message.getPayload() + ")");
            queue.ack(message.getId());
        }

        System.out.printf("%nSummary: %d unique orders processed, %d total receive() calls, %d duplicate deliveries handled.%n",
                processedIds.size(), receiveCalls.get(), duplicateDeliveries.get());

        queue.shutdown();
    }
}
