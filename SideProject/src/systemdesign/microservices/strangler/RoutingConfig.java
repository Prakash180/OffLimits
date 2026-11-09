package com.example.strangler.config;

import org.springframework.stereotype.Service;
import java.util.HashMap;
import java.util.Map;

/**
 * Routing Configuration / Feature Flags
 * 
 * Determines which services are enabled and ready to receive traffic.
 * 
 * During migration, use these flags to gradually shift traffic:
 * - Phase 1: All services disabled → all traffic to monolith
 * - Phase 2: USER_SERVICE enabled → canary test with 10% traffic
 * - Phase 3: Increase to 50% traffic
 * - Phase 4: 100% traffic to new service
 * - Phase 5: Decommission monolith for that service
 * 
 * Can be driven by:
 * - Environment variables
 * - Application properties
 * - Database flags
 * - Feature flag service (LaunchDarkly, Unleash, etc.)
 */
@Service
public class RoutingConfig {
    
    private Map<String, Boolean> serviceStatus = new HashMap<>();
    private Map<String, Integer> serviceTrafficPercentage = new HashMap<>();

    public RoutingConfig() {
        // Initialize from environment variables
        initializeServiceStatus();
        initializeTrafficPercentages();
    }

    /**
     * Read service enabled status from environment
     */
    private void initializeServiceStatus() {
        // Check env var: USER_SERVICE_ENABLED=true/false
        this.serviceStatus.put("USER_SERVICE", 
            Boolean.parseBoolean(System.getenv().getOrDefault("USER_SERVICE_ENABLED", "false")));
        
        this.serviceStatus.put("ORDER_SERVICE", 
            Boolean.parseBoolean(System.getenv().getOrDefault("ORDER_SERVICE_ENABLED", "false")));
        
        this.serviceStatus.put("PAYMENT_SERVICE", 
            Boolean.parseBoolean(System.getenv().getOrDefault("PAYMENT_SERVICE_ENABLED", "false")));
        
        System.out.println("RoutingConfig initialized:");
        serviceStatus.forEach((service, enabled) -> 
            System.out.println("  " + service + ": " + (enabled ? "ENABLED" : "DISABLED"))
        );
    }

    /**
     * Read traffic percentage allocation from environment
     * Example: USER_SERVICE_TRAFFIC=50 means 50% goes to new service, 50% to monolith
     */
    private void initializeTrafficPercentages() {
        this.serviceTrafficPercentage.put("USER_SERVICE", 
            Integer.parseInt(System.getenv().getOrDefault("USER_SERVICE_TRAFFIC", "0")));
        
        this.serviceTrafficPercentage.put("ORDER_SERVICE", 
            Integer.parseInt(System.getenv().getOrDefault("ORDER_SERVICE_TRAFFIC", "0")));
        
        this.serviceTrafficPercentage.put("PAYMENT_SERVICE", 
            Integer.parseInt(System.getenv().getOrDefault("PAYMENT_SERVICE_TRAFFIC", "0")));
    }

    /**
     * Check if a service is enabled
     */
    public boolean isServiceEnabled(String serviceName) {
        return serviceStatus.getOrDefault(serviceName, false);
    }

    /**
     * Get traffic percentage for a service
     * Returns: 0-100 (percentage of traffic that should go to new service)
     * Example: 30 means 30% to new service, 70% to monolith
     */
    public int getTrafficPercentage(String serviceName) {
        return serviceTrafficPercentage.getOrDefault(serviceName, 0);
    }

    /**
     * Should this request go to new service or monolith?
     * Uses traffic percentage to canary deploy
     */
    public boolean shouldRouteToNewService(String serviceName) {
        if (!isServiceEnabled(serviceName)) {
            return false;
        }
        
        int trafficPercentage = getTrafficPercentage(serviceName);
        if (trafficPercentage >= 100) {
            return true;  // 100% → always new service
        }
        if (trafficPercentage <= 0) {
            return false; // 0% → always monolith
        }
        
        // For canary: random decision based on percentage
        int random = (int) (Math.random() * 100);
        return random < trafficPercentage;
    }

    /**
     * Enable a service (typically called by admin/deployment)
     */
    public synchronized void enableService(String serviceName) {
        this.serviceStatus.put(serviceName, true);
        System.out.println("✓ ENABLED routing to " + serviceName);
    }

    /**
     * Disable a service (emergency rollback)
     */
    public synchronized void disableService(String serviceName) {
        this.serviceStatus.put(serviceName, false);
        System.out.println("✗ DISABLED routing to " + serviceName + " - falling back to monolith");
    }

    /**
     * Set traffic percentage for gradual rollout
     */
    public synchronized void setTrafficPercentage(String serviceName, int percentage) {
        if (percentage < 0 || percentage > 100) {
            throw new IllegalArgumentException("Traffic percentage must be 0-100");
        }
        this.serviceTrafficPercentage.put(serviceName, percentage);
        System.out.println("→ " + serviceName + " traffic set to " + percentage + "%");
    }

    /**
     * Get current routing status (for monitoring/debugging)
     */
    public Map<String, Object> getRoutingStatus(String serviceName) {
        Map<String, Object> status = new HashMap<>();
        status.put("enabled", isServiceEnabled(serviceName));
        status.put("trafficPercentage", getTrafficPercentage(serviceName));
        status.put("active", shouldRouteToNewService(serviceName));
        return status;
    }
}
