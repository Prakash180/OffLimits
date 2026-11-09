package com.example.strangler;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.client.RestClientException;

/**
 * Strangler Routing Facade
 * 
 * Routes requests to either:
 * - New Microservices (if available)
 * - Legacy Monolith (fallback)
 * 
 * This is the core of the Strangler Pattern migration strategy.
 * Gradually shift traffic from monolith to new services without downtime.
 */
@RestController
@RequestMapping("/api")
public class StranglerFacade {

    @Autowired
    private RestTemplate restTemplate;

    @Autowired
    private RoutingConfig routingConfig;

    // ===== USER ENDPOINTS =====
    
    /**
     * GET /api/users/{id}
     * Route to User Service if enabled, otherwise monolith
     */
    @GetMapping("/users/{id}")
    public ResponseEntity<?> getUser(@PathVariable String id) {
        if (routingConfig.isServiceEnabled("USER_SERVICE")) {
            try {
                return routeToNewService("http://user-service:8001/users/" + id);
            } catch (RestClientException e) {
                System.out.println("User Service failed, falling back to monolith");
                return routeToMonolith("http://monolith:8080/users/" + id);
            }
        }
        return routeToMonolith("http://monolith:8080/users/" + id);
    }

    /**
     * POST /api/users
     * Always write to monolith first (safer during migration)
     * Then async update new service
     */
    @PostMapping("/users")
    public ResponseEntity<?> createUser(@RequestBody UserRequest request) {
        // Write to monolith (authoritative source during migration)
        ResponseEntity<?> result = routeToMonolith(
            "http://monolith:8080/users",
            "POST",
            request
        );
        
        // If monolith succeeds and User Service is enabled, also write to new service
        if (result.getStatusCode().is2xxSuccessful() && 
            routingConfig.isServiceEnabled("USER_SERVICE")) {
            asyncUpdateNewService("http://user-service:8001/users", request);
        }
        
        return result;
    }

    /**
     * PUT /api/users/{id}
     * Dual write: monolith + new service (during migration phase)
     */
    @PutMapping("/users/{id}")
    public ResponseEntity<?> updateUser(@PathVariable String id, @RequestBody UserRequest request) {
        // Primary write to monolith
        ResponseEntity<?> monolithResult = routeToMonolith(
            "http://monolith:8080/users/" + id,
            "PUT",
            request
        );
        
        // Secondary write to new service (if enabled and monolith succeeded)
        if (monolithResult.getStatusCode().is2xxSuccessful() && 
            routingConfig.isServiceEnabled("USER_SERVICE")) {
            try {
                routeToNewService(
                    "http://user-service:8001/users/" + id,
                    "PUT",
                    request
                );
            } catch (RestClientException e) {
                // Log but don't fail the request
                System.err.println("Failed to update new User Service: " + e.getMessage());
                // TODO: Queue this for async retry
            }
        }
        
        return monolithResult;
    }

    // ===== ORDER ENDPOINTS =====
    
    /**
     * GET /api/orders/{id}
     * Route to Order Service if enabled, otherwise monolith
     */
    @GetMapping("/orders/{id}")
    public ResponseEntity<?> getOrder(@PathVariable String id) {
        if (routingConfig.isServiceEnabled("ORDER_SERVICE")) {
            try {
                return routeToNewService("http://order-service:8002/orders/" + id);
            } catch (RestClientException e) {
                System.out.println("Order Service failed, falling back to monolith");
                return routeToMonolith("http://monolith:8080/orders/" + id);
            }
        }
        return routeToMonolith("http://monolith:8080/orders/" + id);
    }

    /**
     * POST /api/orders
     * Route to Order Service if enabled, otherwise monolith
     */
    @PostMapping("/orders")
    public ResponseEntity<?> createOrder(@RequestBody OrderRequest request) {
        if (routingConfig.isServiceEnabled("ORDER_SERVICE")) {
            try {
                return routeToNewService("http://order-service:8002/orders", "POST", request);
            } catch (RestClientException e) {
                System.out.println("Order Service failed, routing to monolith");
                return routeToMonolith("http://monolith:8080/orders", "POST", request);
            }
        }
        return routeToMonolith("http://monolith:8080/orders", "POST", request);
    }

    // ===== HELPER METHODS =====
    
    /**
     * Route GET request to new microservice
     */
    private ResponseEntity<?> routeToNewService(String url) {
        return restTemplate.getForEntity(url, Object.class);
    }

    /**
     * Route POST/PUT request to new microservice
     */
    private ResponseEntity<?> routeToNewService(String url, String method, Object body) {
        if ("POST".equals(method)) {
            return restTemplate.postForEntity(url, body, Object.class);
        } else if ("PUT".equals(method)) {
            return restTemplate.exchange(url, org.springframework.http.HttpMethod.PUT, 
                new org.springframework.http.HttpEntity<>(body), Object.class);
        }
        throw new IllegalArgumentException("Unsupported method: " + method);
    }

    /**
     * Route GET request to legacy monolith
     */
    private ResponseEntity<?> routeToMonolith(String url) {
        return restTemplate.getForEntity(url, Object.class);
    }

    /**
     * Route POST/PUT request to legacy monolith
     */
    private ResponseEntity<?> routeToMonolith(String url, String method, Object body) {
        if ("POST".equals(method)) {
            return restTemplate.postForEntity(url, body, Object.class);
        } else if ("PUT".equals(method)) {
            return restTemplate.exchange(url, org.springframework.http.HttpMethod.PUT, 
                new org.springframework.http.HttpEntity<>(body), Object.class);
        }
        throw new IllegalArgumentException("Unsupported method: " + method);
    }

    /**
     * Asynchronously update new service (fire and forget)
     * If it fails, we don't block the response to the client
     * But we should log it for monitoring/alerting
     */
    private void asyncUpdateNewService(String url, Object body) {
        new Thread(() -> {
            try {
                restTemplate.postForEntity(url, body, Object.class);
                System.out.println("✓ Async update to new service succeeded: " + url);
            } catch (RestClientException e) {
                System.err.println("✗ Async update to new service failed: " + url + " - " + e.getMessage());
                // TODO: Send to dead letter queue for manual retry
            }
        }).start();
    }
}
