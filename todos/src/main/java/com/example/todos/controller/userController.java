package com.example.todos.controller;

import com.example.todos.entity.users;
import com.example.todos.service.userService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/users")
public class userController {

    @Autowired
    private userService userService;

    @GetMapping("/{id}")
    public users getUsers(@PathVariable Long id){
        return userService.getUser(id);
    }

    @PostMapping
    public users createUser(@RequestParam String name, @RequestParam String email){
        return userService.createUser(name,email);
    }

    @PutMapping("/{id}")
    public users updateUser(@PathVariable Long id, @RequestParam String email){
        return userService.updateUserEmail(id,email);
    }

    @DeleteMapping("/{id}")
    public void deleteUser(@PathVariable Long id){
        userService.deleteUser(id);
    }
}
