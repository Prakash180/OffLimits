// Routing Facade: Direct Traffic Between Legacy Monolith and New Services
// This example uses Spring Boot to create a routing layer for the Strangler Pattern

package com.example.strangler;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

/**
 * Strangler Routing Facade
 * 
 * Routes requests to either:
 * - New Microservices (if available)
 * - Legacy Monolith (fallback)
 */
@RestController
@RequestMapping("/api")
public class StranglerFacade {

    @Autowired
    private RestTemplate restTemplate;

    @Autowired
    private RoutingConfig routingConfig;

    // ===== USER ENDPOINTS =====
    
    @GetMapping("/users/{id}")
    public ResponseEntity<?> getUser(@PathVariable String id) {
        // Check if User Service is available (new service)
        if (routingConfig.isServiceEnabled("USER_SERVICE")) {
            return routeToNewService("http://user-service:8001/users/" + id);
        }
        // Fallback to monolith (legacy)
        return routeToMonolith("http://monolith:8080/users/" + id);
    }

    @PostMapping("/users")
    public ResponseEntity<?> createUser(@RequestBody UserRequest request) {
        // Always route writes to monolith first (safer during migration)
        // But update new service asynchronously
        ResponseEntity<?> result = routeToMonolith(
            "http://monolith:8080/users",
            "POST",
            request
        );
        
        // If monolith succeeds, also write to new service (async)
        if (result.getStatusCode().is2xxSuccessful()) {
            asyncUpdateNewService("http://user-service:8001/users", request);
        }
        
        return result;
    }

    @PutMapping("/users/{id}")
    public ResponseEntity<?> updateUser(@PathVariable String id, @RequestBody UserRequest request) {
        // Dual write: monolith + new service (synchronously during migration)
        ResponseEntity<?> monolithResult = routeToMonolith(
            "http://monolith:8080/users/" + id,
            "PUT",
            request
        );
        
        if (monolithResult.getStatusCode().is2xxSuccessful()) {
            // Also write to new service if monolith succeeds
            try {
                routeToNewService(
                    "http://user-service:8001/users/" + id,
                    "PUT",
                    request
                );
            } catch (Exception e) {
                // Log but don't fail the main request
                System.err.println("Failed to update new service: " + e.getMessage());
            }
        }
        
        return monolithResult;
    }

    // ===== ORDER ENDPOINTS =====
    
    @GetMapping("/orders/{id}")
    public ResponseEntity<?> getOrder(@PathVariable String id) {
        // Route reads to new service if available
        if (routingConfig.isServiceEnabled("ORDER_SERVICE")) {
            try {
                return routeToNewService("http://order-service:8002/orders/" + id);
            } catch (Exception e) {
                // If new service fails, fallback to monolith
                System.out.println("New Order Service failed, falling back to monolith");
                return routeToMonolith("http://monolith:8080/orders/" + id);
            }
        }
        return routeToMonolith("http://monolith:8080/orders/" + id);
    }

    @PostMapping("/orders")
    public ResponseEntity<?> createOrder(@RequestBody OrderRequest request) {
        if (routingConfig.isServiceEnabled("ORDER_SERVICE")) {
            return routeToNewService("http://order-service:8002/orders", "POST", request);
        }
        return routeToMonolith("http://monolith:8080/orders", "POST", request);
    }

    // ===== HELPER METHODS =====
    
    /**
     * Route request to new microservice
     */
    private ResponseEntity<?> routeToNewService(String url) {
        return restTemplate.getForEntity(url, Object.class);
    }

    private ResponseEntity<?> routeToNewService(String url, String method, Object body) {
        if ("POST".equals(method)) {
            return restTemplate.postForEntity(url, body, Object.class);
        } else if ("PUT".equals(method)) {
            return restTemplate.exchange(url, org.springframework.http.HttpMethod.PUT, 
                new org.springframework.http.HttpEntity<>(body), Object.class).getBody() != null 
                ? ResponseEntity.ok().build() 
                : ResponseEntity.notFound().build();
        }
        return ResponseEntity.badRequest().build();
    }

    /**
     * Route request to legacy monolith
     */
    private ResponseEntity<?> routeToMonolith(String url) {
        return restTemplate.getForEntity(url, Object.class);
    }

    private ResponseEntity<?> routeToMonolith(String url, String method, Object body) {
        if ("POST".equals(method)) {
            return restTemplate.postForEntity(url, body, Object.class);
        } else if ("PUT".equals(method)) {
            return restTemplate.exchange(url, org.springframework.http.HttpMethod.PUT, 
                new org.springframework.http.HttpEntity<>(body), Object.class).getBody() != null 
                ? ResponseEntity.ok().build() 
                : ResponseEntity.notFound().build();
        }
        return ResponseEntity.badRequest().build();
    }

    /**
     * Asynchronously update new service (fire and forget)
     */
    private void asyncUpdateNewService(String url, Object body) {
        new Thread(() -> {
            try {
                restTemplate.postForEntity(url, body, Object.class);
            } catch (Exception e) {
                System.err.println("Async update to new service failed: " + e.getMessage());
            }
        }).start();
    }
}

// ===== DATA MODELS =====

class UserRequest {
    private String name;
    private String email;
    private String city;

    public UserRequest() {}

    public UserRequest(String name, String email, String city) {
        this.name = name;
        this.email = email;
        this.city = city;
    }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    
    public String getCity() { return city; }
    public void setCity(String city) { this.city = city; }
}

class OrderRequest {
    private String userId;
    private String productId;
    private int quantity;

    public OrderRequest() {}

    public OrderRequest(String userId, String productId, int quantity) {
        this.userId = userId;
        this.productId = productId;
        this.quantity = quantity;
    }

    public String getUserId() { return userId; }
    public void setUserId(String userId) { this.userId = userId; }
    
    public String getProductId() { return productId; }
    public void setProductId(String productId) { this.productId = productId; }
    
    public int getQuantity() { return quantity; }
    public void setQuantity(int quantity) { this.quantity = quantity; }
}

// ===== ROUTING CONFIG (Feature Flag) =====

package com.example.strangler.config;

import org.springframework.stereotype.Service;
import java.util.HashMap;
import java.util.Map;

/**
 * Routing Configuration
 * 
 * Determines which services are enabled/ready
 * Can be driven by:
 * - Environment variables
 * - Database flags
 * - Feature flag service (LaunchDarkly, etc.)
 */
@Service
public class RoutingConfig {
    
    private Map<String, Boolean> serviceStatus = new HashMap<>();

    public RoutingConfig() {
        // Initialize service status from environment/config
        this.serviceStatus.put("USER_SERVICE", Boolean.parseBoolean(System.getenv("USER_SERVICE_ENABLED") ?? "false"));
        this.serviceStatus.put("ORDER_SERVICE", Boolean.parseBoolean(System.getenv("ORDER_SERVICE_ENABLED") ?? "false"));
        this.serviceStatus.put("PAYMENT_SERVICE", Boolean.parseBoolean(System.getenv("PAYMENT_SERVICE_ENABLED") ?? "false"));
    }

    /**
     * Check if a service is enabled and ready
     */
    public boolean isServiceEnabled(String serviceName) {
        return serviceStatus.getOrDefault(serviceName, false);
    }

    /**
     * Enable a service (called during rollout)
     */
    public void enableService(String serviceName) {
        this.serviceStatus.put(serviceName, true);
        System.out.println("✓ Enabled routing to " + serviceName);
    }

    /**
     * Disable a service (emergency rollback)
     */
    public void disableService(String serviceName) {
        this.serviceStatus.put(serviceName, false);
        System.out.println("✗ Disabled routing to " + serviceName + " - falling back to monolith");
    }
}

// ===== SPRING BOOT CONFIG =====

package com.example.strangler.config;

import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestTemplate;

@Configuration
public class StranglerConfig {

    @Bean
    public RestTemplate restTemplate(RestTemplateBuilder builder) {
        return builder
            .setConnectTimeout(5000)      // Connection timeout: 5 sec
            .setReadTimeout(10000)        // Read timeout: 10 sec
            .build();
    }
}

// ===== USAGE EXAMPLE =====

/**
 * How to use during migration:
 * 
 * Phase 1: All traffic to monolith
 *   - USER_SERVICE_ENABLED=false
 *   - ORDER_SERVICE_ENABLED=false
 *   - All requests route to monolith
 * 
 * Phase 2: Canary test User Service (10% traffic)
 *   - USER_SERVICE_ENABLED=true
 *   - Random 10% of requests go to User Service
 *   - 90% still go to monolith
 *   - Monitor for errors in new service
 * 
 * Phase 3: Increase to 50% traffic to User Service
 *   - USER_SERVICE_ENABLED=true
 *   - 50% traffic to User Service, 50% to monolith
 *   - Compare response times, error rates
 * 
 * Phase 4: 100% traffic to User Service
 *   - USER_SERVICE_ENABLED=true
 *   - All reads/writes go to User Service
 *   - Keep monolith running as backup
 * 
 * Phase 5: Decommission monolith for User endpoints
 *   - Remove User Service endpoint from strangler facade
 */
