package com.example.todos.controller;

import com.example.todos.entity.todos;
import com.example.todos.service.todoService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/todos")
public class todoController {

    @Autowired
    private todoService todoService;

    @GetMapping("/{id}")
    public List<todos> getTodosforUser(@PathVariable Long id){
        return todoService.getTodosByUser(id);
    }

    @PostMapping
    public todos createTodo(@RequestParam Long userId, @RequestParam String todoText){
        return todoService.addTodos(userId, todoText);
    }

    @PutMapping("/{id}")
    public todos updateTodotoCompleted(@PathVariable Long id){
        return todoService.setTodoCompleted(id);
    }

    @DeleteMapping("/{id}")
    public void deleteTodo(@PathVariable Long id){
        todoService.deleteTodo(id);
    }

    @PutMapping("/{id}/text")
    public todos updateTodoText(@PathVariable Long id, @RequestParam String todoText){
        return todoService.updateTodoMessage(id,todoText);
    }
    
}
