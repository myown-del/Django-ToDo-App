import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
@pytest.mark.ui
class TestVisualStates:
    def test_incomplete_todo_visual_state(self, todo_page):
        todo_page.goto()
        
        test_text = "Incomplete task"
        todo_page.add_todo(test_text)
        
        link = todo_page.page.locator(f'a:has(li:has-text("{test_text}"))')
        assert link.count() > 0, "Незавершенная задача должна быть обернута в тег <a>"
        
        li_element = todo_page.page.locator(f'li.list-group-item:has-text("{test_text}")')
        assert li_element.count() > 0, "Должен иметь класс list-group-item"
        
        completed = todo_page.page.locator(f'li.todo-completed:has-text("{test_text}")')
        assert completed.count() == 0, "НЕ должен иметь класс todo-completed"
    
    def test_completed_todo_visual_state(self, todo_page):
        todo_page.goto()
        
        test_text = "Completed task"
        todo_page.add_todo(test_text)
        todo_page.complete_todo(test_text)
        
        link = todo_page.page.locator(f'a:has(li:has-text("{test_text}"))')
        assert link.count() == 0, "Завершенная задача НЕ должна быть обернута в ссылку"
        
        completed_li = todo_page.page.locator(f'li.todo-completed:has-text("{test_text}")')
        assert completed_li.count() > 0, "Должен иметь класс todo-completed"
        
        class_attr = completed_li.get_attribute("class")
        assert "list-group-item" in class_attr, "Должен иметь класс list-group-item"
        assert "todo-completed" in class_attr, "Должен иметь класс todo-completed"
    
    def test_css_class_transitions(self, todo_page):
        todo_page.goto()
        
        test_text = "Transition test"
        todo_page.add_todo(test_text)
        
        li_before = todo_page.page.locator(f'li:has-text("{test_text}")').first
        classes_before = li_before.get_attribute("class")
        assert "todo-completed" not in classes_before, "Изначально не должна быть завершенной"
        
        todo_page.complete_todo(test_text)
        
        li_after = todo_page.page.locator(f'li:has-text("{test_text}")').first
        classes_after = li_after.get_attribute("class")
        assert "todo-completed" in classes_after, "Должна иметь класс завершенности после завершения"


@pytest.mark.e2e
@pytest.mark.ui
class TestInteractiveElements:
    def test_incomplete_todo_is_clickable(self, todo_page):
        todo_page.goto()
        
        test_text = "Clickable todo"
        todo_page.add_todo(test_text)
        
        clickable = todo_page.page.locator(f'a:has(li:has-text("{test_text}"))')
        
        assert clickable.count() > 0, "Кликабельный элемент должен существовать"
        assert clickable.is_visible(), "Должен быть видимым"
        
        # Проверяем наличие href
        href = clickable.get_attribute("href")
        assert href, "Должен иметь атрибут href"
    
    def test_completed_todo_is_not_clickable(self, todo_page):
        todo_page.goto()
        
        test_text = "Not clickable"
        todo_page.add_todo(test_text)
        todo_page.complete_todo(test_text)
        
        # Проверяем отсутствие ссылки
        link = todo_page.page.locator(f'a:has(li:has-text("{test_text}"))')
        assert link.count() == 0, "Завершенная задача не должна быть ссылкой"
        
        # Проверяем, что  li
        plain_li = todo_page.page.locator(f'li.todo-completed:has-text("{test_text}")')
        assert plain_li.count() > 0, "Должна существовать как обычный элемент li"
    
    def test_clicking_incomplete_todo_marks_complete(self, todo_page):
        todo_page.goto()
        
        test_text = "Click to complete"
        todo_page.add_todo(test_text)
        
        assert todo_page.is_todo_clickable(test_text), "Изначально должна быть кликабельной"
        
        clickable = todo_page.page.locator(f'a:has(li:has-text("{test_text}"))')
        clickable.click()
        todo_page.page.wait_for_load_state("networkidle")
        
        # Проверяем, что теперь не кликабельна
        assert not todo_page.is_todo_clickable(test_text), "Не должна быть кликабельной после завершения"
        assert todo_page.is_todo_completed(test_text), "Должна быть отмечена как завершенная"
    
    def test_button_elements_are_visible(self, todo_page):
        todo_page.goto()
        
        add_btn = todo_page.page.locator('button:has-text("ADD")')
        assert add_btn.is_visible(), "Кнопка ADD должна быть видимой"
        
        delete_completed_btn = todo_page.page.locator('button:has-text("DELETE COMPLETED")')
        assert delete_completed_btn.is_visible(), "Кнопка DELETE COMPLETED должна быть видимой"
        
        delete_all_btn = todo_page.page.locator('button:has-text("DELETE ALL")')
        assert delete_all_btn.is_visible(), "Кнопка DELETE ALL должна быть видимой"
    
    def test_button_click_actions(self, todo_page):
        todo_page.goto()
        
        todo_page.page.locator('input[name="text"]').fill("Button test")
        todo_page.page.locator('button:has-text("ADD")').click()
        todo_page.page.wait_for_load_state("networkidle")
        assert todo_page.get_todo_count() == 1, "Кнопка ADD должна добавлять задачу"
        
        todo_page.page.locator('button:has-text("DELETE ALL")').click()
        todo_page.page.wait_for_load_state("networkidle")
        assert todo_page.get_todo_count() == 0, "DELETE ALL должна удалять все задачи"
        
        todo_page.add_todo("Test 1")
        todo_page.add_todo("Test 2")
        todo_page.complete_todo("Test 1")
        
        todo_page.page.locator('button:has-text("DELETE COMPLETED")').click()
        todo_page.page.wait_for_load_state("networkidle")
        assert todo_page.get_todo_count() == 1, "DELETE COMPLETED должна удалять только завершенные"
        assert "Test 2" in todo_page.get_all_todos(), "Незавершенная задача должна остаться"

