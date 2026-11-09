package com.example.strangler.model;

/**
 * User Request DTO
 * 
 * Data Transfer Object for creating/updating users
 */
public class UserRequest {
    private String id;
    private String name;
    private String email;
    private String city;

    // Constructors
    public UserRequest() {}

    public UserRequest(String name, String email, String city) {
        this.name = name;
        this.email = email;
        this.city = city;
    }

    public UserRequest(String id, String name, String email, String city) {
        this.id = id;
        this.name = name;
        this.email = email;
        this.city = city;
    }

    // Getters and Setters
    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getCity() {
        return city;
    }

    public void setCity(String city) {
        this.city = city;
    }

    @Override
    public String toString() {
        return "UserRequest{" +
                "id='" + id + '\'' +
                ", name='" + name + '\'' +
                ", email='" + email + '\'' +
                ", city='" + city + '\'' +
                '}';
    }
}
