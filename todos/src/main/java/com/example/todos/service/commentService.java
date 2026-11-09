package com.example.todos.service;

import com.example.todos.entity.comment;
import com.example.todos.entity.post;
import com.example.todos.entity.users;
import com.example.todos.repository.commentRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
public class commentService {

    @Autowired
    private commentRepository commentRepository;
    
    @Autowired
    private postService postService;
    
    @Autowired
    private userService userService;

    // CREATE - Create comment with two relationships (post + author)
    public comment createComment(Long postId, Long authorId, String commentText) {
        post post = postService.getPostById(postId);      // Get parent 1
        users author = userService.getUser(authorId);     // Get parent 2
        
        comment newComment = new comment();
        newComment.setPost(post);        // Set relationship 1
        newComment.setAuthor(author);    // Set relationship 2
        newComment.setComment(commentText);
        
        return commentRepository.save(newComment);
    }

    // READ - Get comment by ID
    public comment getCommentById(Long commentId) {
        return commentRepository.findById(commentId)
                .orElseThrow(() -> new IllegalArgumentException("comment doesn't exist"));
    }

    // READ - Get all comments on a post
    public List<comment> getCommentsByPost(Long postId) {
        post post = postService.getPostById(postId);
        return commentRepository.findByPost(post);
    }

    // READ - Get all comments by an author
    public List<comment> getCommentsByAuthor(Long authorId) {
        users author = userService.getUser(authorId);
        return commentRepository.findByAuthor(author);
    }

    // UPDATE - Update comment text
    public comment updateCommentText(Long commentId, String newCommentText) {
        comment comment = getCommentById(commentId);
        comment.setComment(newCommentText);
        return commentRepository.save(comment);
    }

    // DELETE - Delete comment
    public void deleteComment(Long commentId) {
        commentRepository.deleteById(commentId);
    }
}
