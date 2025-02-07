from gro import Wrapper as grow
from gro import Block
import gradio as gr

import os

print(f"Current working directory: {os.getcwd()}")
print(f"os.syspath : {os.sys.path}")

class HelloBlock(Block):
    """
    A custom block that defines the UI layout for the todo application.
    """
    todo_textbox = grow(gr.Textbox, show_label=False, placeholder="E.g. Buy groceries")
    add_button = grow(gr.Button, value="Add task")
    tasks_markdown = grow(gr.Markdown)

    def layout(self):
        """
        Defines the layout of the UI components.
        """
        with gr.Row():
            with gr.Column(scale=1):
                with gr.Group():
                    self.todo_textbox()
                    self.add_button()
            with gr.Column(scale=4):
                gr.Markdown("### Tasks")
                self.tasks_markdown()

class Todo:
    """
    A class to manage the todo tasks.
    """
    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        self.tasks.append({"task": task, "completed": False})

    def get_task_markdown(self):
        return "\n".join(f"- {t['task']}" for t in self.tasks if not t["completed"])

class Application:
    """
    The main application class that ties the UI and the todo logic together.
    """
    def __init__(self):
        self.todo = Todo()

        # ui configuration
        self.ui = HelloBlock(title="gro Todo App")

        # populate some initial data for model
        self.todo.add_task("Wake up at 8. (Default task)")

        # ui <-> model configuration
        # bind data source
        self.ui.tasks_markdown.source(self.todo.get_task_markdown)

        # set event listeners
        self.ui.add_button.click(fn=self.add_button_click, inputs=[self.ui.todo_textbox],
                                 outputs=[self.ui.tasks_markdown])
        self.ui.add_button.click(fn=self.add_button_click_then, outputs=[self.ui.todo_textbox], show_progress="hidden")
        
    def add_button_click(self, task):
        # Handles the event when the add button is clicked to update tasks_markdown.
        self.todo.add_task(task)
        return self.todo.get_task_markdown()
    
    def add_button_click_then(self):
        # Handles the event when the add button is clicked to clear the todo_textbox.
        return ""

    def run(self):
        # following should be the last call as it doesn't return.
        self.ui.start(inbrowser=True)

if __name__ == "__main__":
    app = Application()
    app.run()