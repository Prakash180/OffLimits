package com.example.todos.service;

import com.example.todos.entity.users;
import com.example.todos.repository.userRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class userService {

    @Autowired
    private  userRepository userRepository;

    public users getUser(Long id){
        users user = userRepository.findById(id).orElseThrow();
        return user;
    }
    public users createUser (String name, String email){
        if(userRepository.existsByName(name))
            throw new IllegalArgumentException("Username taken");

        users user = new users();
        user.setName(name);
        user.setEmail(email);

        return userRepository.save(user);
    }

    public users updateUserEmail (Long id, String email){
        if(!userRepository.existsById(id))
            throw new IllegalArgumentException("User doesn't exist");

        users user = userRepository.findById(id).orElseThrow(() -> new IllegalArgumentException("User doesn't exist"));
        user.setEmail(email);
        return userRepository.save(user);
    }

    public void deleteUser(Long id){
        userRepository.deleteById(id);
    }


}
