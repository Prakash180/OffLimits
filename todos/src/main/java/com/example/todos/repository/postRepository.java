package com.example.todos.repository;

import com.example.todos.entity.post;
import com.example.todos.entity.users;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface postRepository extends JpaRepository<post, Long> {
    List<post> findByAuthor(users author);
    List<post> findByAuthorOrderByCreatedAtDesc(users author);
    List<post> findAllByOrderByCreatedAtDesc();
}
