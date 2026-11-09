package systemdesign.messagequeue;

import java.util.Map;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

/**
 * A minimal in-memory message queue that mimics the "at-least-once" delivery
 * model used by real brokers like SQS:
 * - A consumer calls receive() and gets a message, which becomes temporarily
 *   invisible to other consumers (its "visibility timeout").
 * - If the consumer finishes, it calls ack(id) to delete the message for good.
 * - If the consumer crashes/never acks in time, a background reaper puts the
 *   message back on the queue so another consumer can pick it up — this is
 *   exactly why consumers must be written to tolerate duplicate delivery.
 */
public class InMemoryMessageQueue {

    private final BlockingQueue<Message> available = new LinkedBlockingQueue<>();
    private final ConcurrentHashMap<String, InFlightEntry> inFlight = new ConcurrentHashMap<>();
    private final long visibilityTimeoutMillis;
    private final ScheduledExecutorService reaper = Executors.newSingleThreadScheduledExecutor();

    public InMemoryMessageQueue(long visibilityTimeoutMillis) {
        this.visibilityTimeoutMillis = visibilityTimeoutMillis;
        // Periodically check for messages whose visibility timeout expired without an ack.
        reaper.scheduleAtFixedRate(this::redeliverExpired, 50, 50, TimeUnit.MILLISECONDS);
    }

    public void send(Message message) {
        available.add(message);
    }

    /** Pulls a message and marks it invisible until ack() is called or the timeout expires. */
    public Message receive(long waitMillis) throws InterruptedException {
        Message message = available.poll(waitMillis, TimeUnit.MILLISECONDS);
        if (message != null) {
            long deadline = System.currentTimeMillis() + visibilityTimeoutMillis;
            inFlight.put(message.getId(), new InFlightEntry(message, deadline));
        }
        return message;
    }

    /** Consumer confirms it finished processing; message is deleted for good. */
    public void ack(String messageId) {
        inFlight.remove(messageId);
    }

    private void redeliverExpired() {
        long now = System.currentTimeMillis();
        for (Map.Entry<String, InFlightEntry> entry : inFlight.entrySet()) {
            InFlightEntry inFlightEntry = entry.getValue();
            if (inFlightEntry.deadline < now) {
                // Atomic remove-if-still-present avoids a race with a concurrent ack().
                if (inFlight.remove(entry.getKey(), inFlightEntry)) {
                    available.add(inFlightEntry.message);
                }
            }
        }
    }

    public void shutdown() {
        reaper.shutdownNow();
    }

    private static final class InFlightEntry {
        final Message message;
        final long deadline;

        InFlightEntry(Message message, long deadline) {
            this.message = message;
            this.deadline = deadline;
        }
    }
}
