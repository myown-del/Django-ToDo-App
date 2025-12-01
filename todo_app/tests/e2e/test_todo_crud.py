import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
class TestTodoCRUDOperations:
    def test_add_single_todo(self, todo_page):
        todo_page.goto()
        
        test_text = "Buy groceries"
        todo_page.add_todo(test_text)
        
        todos = todo_page.get_all_todos()
        assert len(todos) == 1, "Должна быть ровно одна задача"
        assert test_text in todos, f"Задача '{test_text}' должна быть в списке"
        
        assert todo_page.is_todo_clickable(test_text), "Новая задача должна быть кликабельной"
        assert not todo_page.is_todo_completed(test_text), "Новая задача не должна быть завершенной"
    
    def test_add_multiple_todos(self, todo_page):
        todo_page.goto()
        
        test_todos = [
            "Clean the house",
            "Write code",
            "Go for a walk"
        ]
        
        for todo_text in test_todos:
            todo_page.add_todo(todo_text)
        
        # Проверить, что все были добавлены
        todos = todo_page.get_all_todos()
        assert len(todos) == 3, "Должно быть три задачи"
        
        for todo_text in test_todos:
            assert todo_text in todos, f"Задача '{todo_text}' должна быть в списке"
            assert todo_page.is_todo_clickable(todo_text), f"Задача '{todo_text}' должна быть кликабельной"
    
    def test_complete_single_todo(self, todo_page):
        todo_page.goto()
        
        test_text = "Finish homework"
        todo_page.add_todo(test_text)
        
        todo_page.complete_todo(test_text)
        
        # Проверить завершение
        assert todo_page.is_todo_completed(test_text), "Задача должна быть отмечена как завершенная"
        assert not todo_page.is_todo_clickable(test_text), "Завершенная задача не должна быть кликабельной"
        assert todo_page.has_css_class(test_text, "todo-completed"), "Должна иметь класс 'todo-completed'"
        
        # Проверить количество
        assert todo_page.get_completed_count() == 1, "Должна быть одна завершенная задача"
        assert todo_page.get_incomplete_count() == 0, "Должно быть ноль незавершенных задач"
    
    def test_complete_multiple_todos_selectively(self, todo_page):
        todo_page.goto()
        
        todos = ["Task A", "Task B", "Task C"]
        for todo in todos:
            todo_page.add_todo(todo)
        
        todo_page.complete_todo("Task A")
        todo_page.complete_todo("Task C")
        
        assert todo_page.is_todo_completed("Task A"), "Task A должна быть завершена"
        assert not todo_page.is_todo_completed("Task B"), "Task B должна быть незавершенной"
        assert todo_page.is_todo_completed("Task C"), "Task C должна быть завершена"
        
        assert not todo_page.is_todo_clickable("Task A"), "Task A не должна быть кликабельной"
        assert todo_page.is_todo_clickable("Task B"), "Task B должна быть кликабельной"
        assert not todo_page.is_todo_clickable("Task C"), "Task C не должна быть кликабельной"
        
        assert todo_page.get_completed_count() == 2, "Должно быть две завершенные задачи"
        assert todo_page.get_incomplete_count() == 1, "Должна быть одна незавершенная задача"
        assert todo_page.get_todo_count() == 3, "Должно быть три задачи всего"
    
    def test_delete_completed_todos(self, todo_page):
        todo_page.goto()
        
        todos = ["Complete me 1", "Keep me", "Complete me 2"]
        for todo in todos:
            todo_page.add_todo(todo)
        
        todo_page.complete_todo("Complete me 1")
        todo_page.complete_todo("Complete me 2")
        
        todo_page.delete_completed()
        
        remaining_todos = todo_page.get_all_todos()
        assert len(remaining_todos) == 1, "Должна остаться одна задача"
        assert "Keep me" in remaining_todos, "Незавершенная задача должна остаться"
        assert "Complete me 1" not in remaining_todos, "Завершенная задача должна быть удалена"
        assert "Complete me 2" not in remaining_todos, "Завершенная задача должна быть удалена"
    
    def test_delete_all_todos(self, todo_page):
        todo_page.goto()
        
        todo_page.add_todo("Todo 1")
        todo_page.add_todo("Todo 2")
        todo_page.add_todo("Todo 3")
        todo_page.complete_todo("Todo 1")
        
        assert todo_page.get_todo_count() == 3, "Должно быть три задачи изначально"
        
        todo_page.delete_all()
        
        assert todo_page.get_todo_count() == 0, "Должно быть ноль задач после удаления всех"
        todos = todo_page.get_all_todos()
        assert len(todos) == 0, "Список задач должен быть пустым"
    
    def test_full_lifecycle_workflow(self, todo_page):
        """
        Полный жизненный цикл от создания до удаления
        
        1. Пользователь добавляет несколько задач
        2. Завершает некоторые задачи
        3. Очищает завершенные задачи
        4. Добавляет больше задач
        5. В конце очищает все задачи
        """
        todo_page.goto()
        
        # 1
        morning_todos = ["Check emails", "Morning meeting", "Code review"]
        for todo in morning_todos:
            todo_page.add_todo(todo)
        
        assert todo_page.get_todo_count() == 3, "Должно быть 3 утренние задачи"
        
        # 2
        todo_page.complete_todo("Check emails")
        todo_page.complete_todo("Morning meeting")
        
        assert todo_page.get_completed_count() == 2, "Должно быть 2 завершенные"
        assert todo_page.get_incomplete_count() == 1, "Должна быть 1 незавершенная"
        
        # 3
        todo_page.delete_completed()
        
        remaining = todo_page.get_all_todos()
        assert len(remaining) == 1, "Должна быть 1 задача после очистки"
        assert "Code review" in remaining, "Code review должен остаться"
        
        # 4
        evening_todos = ["Prepare presentation", "Update documentation"]
        for todo in evening_todos:
            todo_page.add_todo(todo)
        
        assert todo_page.get_todo_count() == 3, "Должно быть 3 задачи всего"
        
        # 5
        todo_page.delete_all()
        
        assert todo_page.get_todo_count() == 0, "Не должно быть задач в конце"
