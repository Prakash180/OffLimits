package systemdesign.consistenthashing;

import java.util.HashMap;
import java.util.Map;

/**
 * Demonstrates why consistent hashing minimizes key remapping compared to plain hash % N,
 * and shows virtual nodes balancing load across servers.
 */
public class ConsistentHashingDemo {

    public static void run() {
        int virtualNodes = 100;
        int numKeys = 10000;

        ConsistentHashRing ring = new ConsistentHashRing(virtualNodes);
        ring.addServer("server-A");
        ring.addServer("server-B");
        ring.addServer("server-C");

        // Snapshot: which server each key maps to before adding a new server.
        Map<String, String> before = new HashMap<>();
        for (int i = 0; i < numKeys; i++) {
            String key = "key-" + i;
            before.put(key, ring.getServer(key));
        }

        // Show load distribution across the 3 servers.
        printDistribution("Before adding server-D", before);

        // Add a 4th server and see how few keys actually move.
        ring.addServer("server-D");

        int movedCount = 0;
        Map<String, String> after = new HashMap<>();
        for (int i = 0; i < numKeys; i++) {
            String key = "key-" + i;
            String server = ring.getServer(key);
            after.put(key, server);
            if (!server.equals(before.get(key))) {
                movedCount++;
            }
        }

        printDistribution("After adding server-D", after);

        double movedPercent = (movedCount * 100.0) / numKeys;
        System.out.printf("%nKeys remapped after adding server-D: %d / %d (%.2f%%)%n",
                movedCount, numKeys, movedPercent);
        System.out.println("(Plain hash % N would remap close to 100% of keys here.)");
    }

    private static void printDistribution(String label, Map<String, String> mapping) {
        Map<String, Integer> counts = new HashMap<>();
        for (String server : mapping.values()) {
            counts.merge(server, 1, Integer::sum);
        }
        System.out.println(label + ": " + counts);
    }
}
