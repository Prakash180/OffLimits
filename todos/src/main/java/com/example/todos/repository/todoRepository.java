package com.example.todos.repository;

import com.example.todos.entity.todos;
import com.example.todos.entity.users;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface todoRepository extends JpaRepository<todos, Long> {
    List<todos> findByUser(users user);
    List<todos> findByUserAndCompleted(users user, boolean completed);
    List<todos> findByCompleted(boolean completed);
}
