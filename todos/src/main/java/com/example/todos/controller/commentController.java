package com.example.todos.controller;

import com.example.todos.entity.comment;
import com.example.todos.service.commentService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/posts/{postId}/comments")
public class commentController {

    @Autowired
    private commentService commentService;

    // GET - Get all comments on a post
    @GetMapping
    public List<comment> getCommentsByPost(@PathVariable Long postId) {
        return commentService.getCommentsByPost(postId);
    }

    // POST - Create comment on a post
    @PostMapping
    public comment createComment(
            @PathVariable Long postId,
            @RequestParam Long authorId,
            @RequestParam String commentText
    ) {
        return commentService.createComment(postId, authorId, commentText);
    }

    // GET - Get single comment on a post
    @GetMapping("/{commentId}")
    public comment getComment(
            @PathVariable Long postId,
            @PathVariable Long commentId
    ) {
        return commentService.getCommentById(commentId);
    }

    // PUT - Update comment on a post
    @PutMapping("/{commentId}")
    public comment updateComment(
            @PathVariable Long postId,
            @PathVariable Long commentId,
            @RequestParam String commentText
    ) {
        return commentService.updateCommentText(commentId, commentText);
    }

    // DELETE - Delete comment on a post
    @DeleteMapping("/{commentId}")
    public void deleteComment(
            @PathVariable Long postId,
            @PathVariable Long commentId
    ) {
        commentService.deleteComment(commentId);
    }
}
