package com.example.todos.service;

import com.example.todos.entity.todos;
import com.example.todos.entity.users;
import com.example.todos.repository.todoRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
public class todoService {

    @Autowired
    private todoRepository todoRepository;
    @Autowired
    private userService userService;


    public todos addTodos(Long id, String toDo) {
        users user = userService.getUser(id);

        todos todo = new todos();
        todo.setUser(user);
        todo.setToDo(toDo);
        return todoRepository.save(todo);
    }

    public todos setTodoCompleted (Long toDoId){
        todos todo = todoRepository.findById(toDoId).orElseThrow(() -> new IllegalArgumentException("todo doesn't exist"));
        todo.setCompleted(true);
        return todoRepository.save(todo);
    }

    public List<todos> getTodosByUser(Long userId) {
        users user = userService.getUser(userId);
        return todoRepository.findByUser(user);
    }

    public todos updateTodoMessage(Long todoId, String todoText){
        todos todo = todoRepository.findById(todoId).orElseThrow(() -> new IllegalArgumentException("todo doesn't exist"));
        todo.setToDo(todoText);
        return todoRepository.save(todo);
    }

    public void deleteTodo (Long todoId){
        todoRepository.deleteById(todoId);
    }

    
}
