package com.example.todos.service;

import com.example.todos.entity.post;
import com.example.todos.entity.users;
import com.example.todos.repository.postRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
public class postService {

    @Autowired
    private postRepository postRepository;
    
    @Autowired
    private userService userService;

    // CREATE - Create new post
    public post createPost(Long authorId, String title, String content) {
        users author = userService.getUser(authorId);
        
        post newPost = new post();
        newPost.setTitle(title);
        newPost.setContent(content);
        newPost.setAuthor(author);
        
        return postRepository.save(newPost);
    }

    // READ - Get post by ID
    public post getPostById(Long postId) {
        return postRepository.findById(postId)
                .orElseThrow(() -> new IllegalArgumentException("post doesn't exist"));
    }

    // READ - Get all posts by author
    public List<post> getPostsByAuthor(Long authorId) {
        users author = userService.getUser(authorId);
        return postRepository.findByAuthor(author);
    }

    // READ - Get all posts (system-wide)
    public List<post> getAllPosts() {
        return postRepository.findAll();
    }

    // UPDATE - Update post title
    public post updatePostTitle(Long postId, String newTitle) {
        post post = getPostById(postId);
        post.setTitle(newTitle);
        return postRepository.save(post);
    }

    // UPDATE - Update post content
    public post updatePostContent(Long postId, String newContent) {
        post post = getPostById(postId);
        post.setContent(newContent);
        return postRepository.save(post);
    }

    // UPDATE - Update both title and content
    public post updatePost(Long postId, String title, String content) {
        post post = getPostById(postId);
        post.setTitle(title);
        post.setContent(content);
        return postRepository.save(post);
    }

    // DELETE - Delete post
    public void deletePost(Long postId) {
        postRepository.deleteById(postId);
    }
}
