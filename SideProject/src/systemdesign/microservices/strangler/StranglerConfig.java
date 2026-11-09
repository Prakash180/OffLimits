package com.example.strangler.config;

import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestTemplate;

/**
 * Spring Boot Configuration for Strangler Facade
 * 
 * Sets up RestTemplate with appropriate timeouts
 * for routing requests between services
 */
@Configuration
public class StranglerConfig {

    /**
     * Create RestTemplate with configured timeouts
     * 
     * - Connection timeout: 5 seconds (time to establish connection)
     * - Read timeout: 10 seconds (time to wait for response)
     */
    @Bean
    public RestTemplate restTemplate(RestTemplateBuilder builder) {
        return builder
            .setConnectTimeout(5000)      // 5 second connection timeout
            .setReadTimeout(10000)        // 10 second read timeout
            .build();
    }
}
