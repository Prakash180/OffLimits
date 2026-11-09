package com.example.todos.repository;

import com.example.todos.entity.comment;
import com.example.todos.entity.post;
import com.example.todos.entity.users;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface commentRepository extends JpaRepository<comment, Long> {
    List<comment> findByPost(post post);
    List<comment> findByAuthor(users author);
    List<comment> findByPostAndAuthor(post post, users author);
}
