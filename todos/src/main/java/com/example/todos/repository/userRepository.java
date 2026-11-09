package com.example.todos.repository;

import com.example.todos.entity.users;
import org.hibernate.mapping.List;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface userRepository extends JpaRepository<users, Long> {
    Optional<users> findByName(String name);
    Optional<users> findByEmail(String email);
    boolean existsByName(String name);
}
