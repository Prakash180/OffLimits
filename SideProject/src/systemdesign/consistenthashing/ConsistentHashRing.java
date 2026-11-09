package systemdesign.consistenthashing;

import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Map;
import java.util.TreeMap;

/**
 * A simple consistent hash ring.
 * - Servers (and their virtual nodes) are placed on a ring of hash values.
 * - A key is routed to the next server clockwise from its own hash position.
 * - Virtual nodes spread each physical server across many points on the ring
 *   so load stays balanced even with few servers.
 */
public class ConsistentHashRing {

    private final int virtualNodesPerServer;
    private final TreeMap<Long, String> ring = new TreeMap<>();

    public ConsistentHashRing(int virtualNodesPerServer) {
        this.virtualNodesPerServer = virtualNodesPerServer;
    }

    // MD5-based hash: plain String.hashCode() is unsuitable here because near-identical
    // strings like "server-A#0" and "server-A#1" produce hash values just 1 apart, which
    // clusters all virtual nodes into a tiny arc instead of spreading them around the ring.
    // MD5 gives well-distributed, unpredictable output so ring positions spread evenly.
    private long hash(String key) {
        try {
            MessageDigest md5 = MessageDigest.getInstance("MD5");
            byte[] digest = md5.digest(key.getBytes());
            // Use the first 4 bytes of the digest as an unsigned 32-bit ring position.
            long h = 0;
            for (int i = 0; i < 4; i++) {
                h = (h << 8) | (digest[i] & 0xff);
            }
            return h;
        } catch (NoSuchAlgorithmException e) {
            throw new IllegalStateException("MD5 not available", e);
        }
    }

    public void addServer(String server) {
        for (int i = 0; i < virtualNodesPerServer; i++) {
            long pos = hash(server + "#" + i);
            ring.put(pos, server);
        }
    }

    public void removeServer(String server) {
        for (int i = 0; i < virtualNodesPerServer; i++) {
            long pos = hash(server + "#" + i);
            ring.remove(pos);
        }
    }

    // Finds the first server clockwise from the key's hash position (wraps around to the start).
    public String getServer(String key) {
        if (ring.isEmpty()) return null;
        long pos = hash(key);
        Map.Entry<Long, String> entry = ring.ceilingEntry(pos);
        if (entry == null) {
            entry = ring.firstEntry();
        }
        return entry.getValue();
    }
}
