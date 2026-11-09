package com.example.todos.controller;

import com.example.todos.entity.post;
import com.example.todos.service.postService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/posts")
public class postController {

    @Autowired
    private postService postService;

    // GET - Get post by ID
    @GetMapping("/{id}")
    public post getPost(@PathVariable Long id) {
        return postService.getPostById(id);
    }

    // GET - Get user's posts
    @GetMapping("/author/{authorId}")
    public List<post> getPostsByAuthor(@PathVariable Long authorId) {
        return postService.getPostsByAuthor(authorId);
    }

    // GET - Get all posts
    @GetMapping
    public List<post> getAllPosts() {
        return postService.getAllPosts();
    }

    // POST - Create post
    @PostMapping
    public post createPost(
            @RequestParam Long authorId,
            @RequestParam String title,
            @RequestParam String content
    ) {
        return postService.createPost(authorId, title, content);
    }

    // PUT - Update post (title and content)
    @PutMapping("/{id}")
    public post updatePost(
            @PathVariable Long id,
            @RequestParam String title,
            @RequestParam String content
    ) {
        return postService.updatePost(id, title, content);
    }

    // PUT - Update title only
    @PutMapping("/{id}/title")
    public post updatePostTitle(
            @PathVariable Long id,
            @RequestParam String title
    ) {
        return postService.updatePostTitle(id, title);
    }

    // PUT - Update content only
    @PutMapping("/{id}/content")
    public post updatePostContent(
            @PathVariable Long id,
            @RequestParam String content
    ) {
        return postService.updatePostContent(id, content);
    }

    // DELETE - Delete post
    @DeleteMapping("/{id}")
    public void deletePost(@PathVariable Long id) {
        postService.deletePost(id);
    }
}
