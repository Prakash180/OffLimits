package com.example.todos.entity;

import jakarta.persistence.*;
import lombok.Data;
import com.fasterxml.jackson.annotation.JsonIgnore;

import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "users")
@Data
public class users {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    Long id;

    @Column
    private String name;

    @Column
    private String email;

    @OneToMany(mappedBy = "user" ,cascade = CascadeType.ALL, orphanRemoval = true)
    @JsonIgnore
    private List<todos> todoslist = new ArrayList<>();

    @OneToMany(mappedBy = "author" ,cascade = CascadeType.ALL, orphanRemoval = true)
    @JsonIgnore
    private List<post> postList = new ArrayList<>();

    @OneToMany(mappedBy = "author" ,cascade = CascadeType.ALL, orphanRemoval = true)
    @JsonIgnore
    private List<comment> commentList = new ArrayList<>();
}
