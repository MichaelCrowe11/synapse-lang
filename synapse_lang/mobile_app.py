"""Mobile App Framework for Synapse Language
Cross-platform mobile interface for Synapse development and execution
"""

import json
import time
import uuid
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum, auto


class AppScreen(Enum):
    """Mobile app screens"""
    HOME = auto()
    EDITOR = auto()
    PROJECTS = auto()
    EXAMPLES = auto()
    QUANTUM = auto()
    COLLABORATION = auto()
    SETTINGS = auto()
    RESULTS = auto()


class ComponentType(Enum):
    """UI component types"""
    BUTTON = auto()
    TEXT_INPUT = auto()
    CODE_EDITOR = auto()
    LIST = auto()
    CARD = auto()
    GRAPH = auto()
    QUANTUM_CIRCUIT = auto()
    TOGGLE = auto()
    SLIDER = auto()
    TAB_BAR = auto()


@dataclass
class UIComponent:
    """Mobile UI component"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    type: ComponentType = ComponentType.BUTTON
    title: str = ""
    content: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)
    children: List['UIComponent'] = field(default_factory=list)
    actions: Dict[str, str] = field(default_factory=dict)  # event -> action_id

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'type': self.type.name,
            'title': self.title,
            'content': self.content,
            'properties': self.properties,
            'children': [child.to_dict() for child in self.children],
            'actions': self.actions
        }


@dataclass
class MobileProject:
    """Mobile project representation"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Untitled Project"
    description: str = ""
    code: str = ""
    language: str = "synapse"
    created: float = field(default_factory=time.time)
    modified: float = field(default_factory=time.time)
    tags: List[str] = field(default_factory=list)
    is_favorite: bool = False
    execution_results: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'code': self.code,
            'language': self.language,
            'created': self.created,
            'modified': self.modified,
            'tags': self.tags,
            'is_favorite': self.is_favorite,
            'execution_results': self.execution_results
        }


class MobileCodeEditor:
    """Mobile-optimized code editor"""

    def __init__(self):
        self.content = ""
        self.cursor_position = 0
        self.syntax_highlighting = True
        self.auto_complete = True
        self.font_size = 14
        self.theme = "dark"

    def insert_text(self, text: str, position: Optional[int] = None):
        """Insert text at cursor or specified position"""
        pos = position if position is not None else self.cursor_position
        self.content = self.content[:pos] + text + self.content[pos:]
        self.cursor_position = pos + len(text)

    def delete_text(self, start: int, end: int):
        """Delete text in range"""
        self.content = self.content[:start] + self.content[end:]
        self.cursor_position = min(self.cursor_position, start)

    def get_current_line(self) -> str:
        """Get current line text"""
        lines = self.content.split('\n')
        line_start = 0
        for i, line in enumerate(lines):
            line_end = line_start + len(line)
            if line_start <= self.cursor_position <= line_end:
                return line
            line_start = line_end + 1  # +1 for newline
        return ""

    def auto_indent(self):
        """Apply auto-indentation"""
        current_line = self.get_current_line()
        indent_level = len(current_line) - len(current_line.lstrip())

        # Add extra indent for control structures
        if current_line.strip().endswith(':') or 'quantum[' in current_line:
            indent_level += 4

        self.insert_text('\n' + ' ' * indent_level)

    def suggest_completion(self, prefix: str) -> List[str]:
        """Get code completion suggestions"""
        synapse_keywords = [
            "let", "def", "if", "then", "else", "for", "in", "while",
            "parallel", "quantum", "hypothesis", "assume", "when", "then",
            "measure", "uncertain", "try", "catch", "import", "export",
            "H", "CNOT", "X", "Y", "Z", "RX", "RY", "RZ"
        ]

        suggestions = []
        for keyword in synapse_keywords:
            if keyword.startswith(prefix.lower()):
                suggestions.append(keyword)

        return suggestions

    def format_code(self) -> str:
        """Format Synapse code for mobile display"""
        lines = self.content.split('\n')
        formatted_lines = []

        for line in lines:
            # Truncate long lines for mobile
            if len(line) > 60:
                line = line[:57] + "..."

            formatted_lines.append(line)

        return '\n'.join(formatted_lines)


class SynapseExamples:
    """Library of Synapse code examples for mobile"""

    @staticmethod
    def get_examples() -> Dict[str, List[Dict[str, Any]]]:
        return {
            "Basic": [
                {
                    "title": "Hello World",
                    "description": "Simple output example",
                    "code": "let message = \"Hello, Synapse!\"\nprint(message)",
                    "difficulty": "beginner"
                },
                {
                    "title": "Variables & Math",
                    "description": "Basic arithmetic operations",
                    "code": "let x = 10\nlet y = 20\nlet sum = x + y\nprint(sum)",
                    "difficulty": "beginner"
                }
            ],
            "Scientific": [
                {
                    "title": "Uncertainty Calculation",
                    "description": "Working with uncertain values",
                    "code": "let measurement = 10.5 ± 0.3\nlet doubled = measurement * 2\nprint(doubled)",
                    "difficulty": "intermediate"
                },
                {
                    "title": "Matrix Operations",
                    "description": "Basic matrix multiplication",
                    "code": "let A = [[1, 2], [3, 4]]\nlet B = [[5, 6], [7, 8]]\nlet C = A @ B\nprint(C)",
                    "difficulty": "intermediate"
                }
            ],
            "Quantum": [
                {
                    "title": "Bell State",
                    "description": "Create quantum entanglement",
                    "code": "quantum[2] {\n    H(q0)\n    CNOT(q0, q1)\n    measure(q0, q1)\n}",
                    "difficulty": "advanced"
                },
                {
                    "title": "Quantum Superposition",
                    "description": "Single qubit superposition",
                    "code": "quantum[1] {\n    H(q0)\n    measure(q0)\n}",
                    "difficulty": "intermediate"
                }
            ],
            "AI & ML": [
                {
                    "title": "Hypothesis Testing",
                    "description": "Scientific hypothesis validation",
                    "code": "hypothesis \"energy_conservation\" {\n    assume total_energy_before\n    when collision_occurs\n    then total_energy_after == total_energy_before\n}",
                    "difficulty": "advanced"
                }
            ]
        }


class MobileUI:
    """Mobile user interface builder"""

    def __init__(self):
        self.screens: Dict[AppScreen, UIComponent] = {}
        self.current_screen = AppScreen.HOME
        self.navigation_stack = [AppScreen.HOME]

    def create_home_screen(self) -> UIComponent:
        """Create home screen UI"""
        home = UIComponent(
            type=ComponentType.LIST,
            title="Synapse Mobile",
            properties={"background": "#1a1a1a", "text_color": "#ffffff"}
        )

        # Welcome card
        welcome_card = UIComponent(
            type=ComponentType.CARD,
            title="Welcome to Synapse",
            content="Scientific programming on the go",
            properties={"gradient": ["#4a90e2", "#7b68ee"]}
        )

        # Quick actions
        new_project_btn = UIComponent(
            type=ComponentType.BUTTON,
            title="New Project",
            properties={"icon": "plus", "color": "#4a90e2"},
            actions={"tap": "navigate_to_editor"}
        )

        examples_btn = UIComponent(
            type=ComponentType.BUTTON,
            title="Examples",
            properties={"icon": "book", "color": "#2ecc71"},
            actions={"tap": "navigate_to_examples"}
        )

        quantum_btn = UIComponent(
            type=ComponentType.BUTTON,
            title="Quantum Lab",
            properties={"icon": "atom", "color": "#9b59b6"},
            actions={"tap": "navigate_to_quantum"}
        )

        collab_btn = UIComponent(
            type=ComponentType.BUTTON,
            title="Collaborate",
            properties={"icon": "users", "color": "#f39c12"},
            actions={"tap": "navigate_to_collaboration"}
        )

        home.children = [welcome_card, new_project_btn, examples_btn, quantum_btn, collab_btn]
        return home

    def create_editor_screen(self) -> UIComponent:
        """Create code editor screen"""
        editor_screen = UIComponent(
            type=ComponentType.LIST,
            title="Code Editor",
            properties={"background": "#0d1117"}
        )

        # Code editor component
        code_editor = UIComponent(
            type=ComponentType.CODE_EDITOR,
            title="editor",
            properties={
                "language": "synapse",
                "theme": "github-dark",
                "font_size": 14,
                "auto_complete": True,
                "line_numbers": True
            }
        )

        # Toolbar
        toolbar = UIComponent(
            type=ComponentType.LIST,
            properties={"orientation": "horizontal", "background": "#21262d"}
        )

        run_btn = UIComponent(
            type=ComponentType.BUTTON,
            title="Run",
            properties={"icon": "play", "color": "#238636"},
            actions={"tap": "execute_code"}
        )

        save_btn = UIComponent(
            type=ComponentType.BUTTON,
            title="Save",
            properties={"icon": "save", "color": "#1f6feb"},
            actions={"tap": "save_project"}
        )

        share_btn = UIComponent(
            type=ComponentType.BUTTON,
            title="Share",
            properties={"icon": "share", "color": "#f78166"},
            actions={"tap": "share_code"}
        )

        toolbar.children = [run_btn, save_btn, share_btn]

        # Quick insert buttons for mobile
        quick_insert = UIComponent(
            type=ComponentType.LIST,
            title="Quick Insert",
            properties={"orientation": "horizontal", "scroll": True}
        )

        quantum_snippet = UIComponent(
            type=ComponentType.BUTTON,
            title="Quantum",
            properties={"size": "small"},
            actions={"tap": "insert_quantum_template"}
        )

        uncertain_snippet = UIComponent(
            type=ComponentType.BUTTON,
            title="Uncertain",
            properties={"size": "small"},
            actions={"tap": "insert_uncertain_template"}
        )

        parallel_snippet = UIComponent(
            type=ComponentType.BUTTON,
            title="Parallel",
            properties={"size": "small"},
            actions={"tap": "insert_parallel_template"}
        )

        quick_insert.children = [quantum_snippet, uncertain_snippet, parallel_snippet]

        editor_screen.children = [toolbar, code_editor, quick_insert]
        return editor_screen

    def create_quantum_screen(self) -> UIComponent:
        """Create quantum circuit designer screen"""
        quantum_screen = UIComponent(
            type=ComponentType.LIST,
            title="Quantum Lab",
            properties={"background": "#0f0f23"}
        )

        # Circuit designer
        circuit_designer = UIComponent(
            type=ComponentType.QUANTUM_CIRCUIT,
            title="Circuit Designer",
            properties={
                "qubits": 3,
                "editable": True,
                "simulation": True
            }
        )

        # Gate palette
        gate_palette = UIComponent(
            type=ComponentType.LIST,
            title="Gates",
            properties={"orientation": "horizontal", "scroll": True}
        )

        gates = ["H", "X", "Y", "Z", "CNOT", "RX", "RY", "RZ"]
        for gate in gates:
            gate_btn = UIComponent(
                type=ComponentType.BUTTON,
                title=gate,
                properties={"style": "quantum_gate", "gate_type": gate},
                actions={"tap": f"add_quantum_gate_{gate.lower()}"}
            )
            gate_palette.children.append(gate_btn)

        # Simulation results
        sim_results = UIComponent(
            type=ComponentType.GRAPH,
            title="Quantum State",
            properties={
                "type": "probability_bars",
                "real_time": True
            }
        )

        quantum_screen.children = [circuit_designer, gate_palette, sim_results]
        return quantum_screen

    def create_examples_screen(self) -> UIComponent:
        """Create examples browser screen"""
        examples_screen = UIComponent(
            type=ComponentType.LIST,
            title="Examples",
            properties={"background": "#fafbfc"}
        )

        examples = SynapseExamples.get_examples()

        for category, example_list in examples.items():
            # Category header
            category_header = UIComponent(
                type=ComponentType.CARD,
                title=category,
                properties={"style": "category_header", "color": "#0969da"}
            )
            examples_screen.children.append(category_header)

            # Examples in category
            for example in example_list:
                example_card = UIComponent(
                    type=ComponentType.CARD,
                    title=example["title"],
                    content=example["description"],
                    properties={
                        "code_preview": example["code"][:50] + "...",
                        "difficulty": example["difficulty"],
                        "full_code": example["code"]
                    },
                    actions={"tap": "load_example"}
                )
                examples_screen.children.append(example_card)

        return examples_screen

    def build_app(self) -> Dict[str, Any]:
        """Build complete mobile app structure"""
        # Create all screens
        self.screens[AppScreen.HOME] = self.create_home_screen()
        self.screens[AppScreen.EDITOR] = self.create_editor_screen()
        self.screens[AppScreen.QUANTUM] = self.create_quantum_screen()
        self.screens[AppScreen.EXAMPLES] = self.create_examples_screen()

        # Create tab bar navigation
        tab_bar = UIComponent(
            type=ComponentType.TAB_BAR,
            properties={"background": "#0d1117", "tint_color": "#58a6ff"}
        )

        tabs = [
            {"title": "Home", "icon": "house", "screen": "HOME"},
            {"title": "Code", "icon": "code", "screen": "EDITOR"},
            {"title": "Quantum", "icon": "atom", "screen": "QUANTUM"},
            {"title": "Examples", "icon": "book", "screen": "EXAMPLES"}
        ]

        for tab in tabs:
            tab_item = UIComponent(
                type=ComponentType.BUTTON,
                title=tab["title"],
                properties={"icon": tab["icon"], "tab_screen": tab["screen"]},
                actions={"tap": f"navigate_to_{tab['screen'].lower()}"}
            )
            tab_bar.children.append(tab_item)

        # App configuration
        app_config = {
            "name": "Synapse Mobile",
            "version": "1.0.0",
            "theme": "dark",
            "screens": {screen.name: component.to_dict()
                       for screen, component in self.screens.items()},
            "navigation": tab_bar.to_dict(),
            "settings": {
                "auto_save": True,
                "syntax_highlighting": True,
                "haptic_feedback": True,
                "dark_mode": True,
                "font_size": 14
            }
        }

        return app_config


class MobileAppManager:
    """Manages mobile app state and actions"""

    def __init__(self):
        self.ui = MobileUI()
        self.editor = MobileCodeEditor()
        self.projects: List[MobileProject] = []
        self.current_project: Optional[MobileProject] = None
        self.app_config = self.ui.build_app()

    def create_project(self, name: str, code: str = "") -> MobileProject:
        """Create new project"""
        project = MobileProject(name=name, code=code)
        self.projects.append(project)
        self.current_project = project
        return project

    def load_project(self, project_id: str):
        """Load existing project"""
        for project in self.projects:
            if project.id == project_id:
                self.current_project = project
                self.editor.content = project.code
                break

    def save_current_project(self):
        """Save current project"""
        if self.current_project:
            self.current_project.code = self.editor.content
            self.current_project.modified = time.time()

    def execute_code(self, code: str) -> Dict[str, Any]:
        """Execute Synapse code (simulated)"""
        execution_result = {
            "timestamp": time.time(),
            "code": code,
            "output": "Execution completed successfully",
            "status": "success",
            "execution_time": 0.15,
            "memory_usage": "2.3 MB"
        }

        # Simulate different outputs based on code content
        if "quantum" in code.lower():
            execution_result["output"] = "Quantum circuit executed\n|00⟩: 0.5\n|11⟩: 0.5"
            execution_result["type"] = "quantum"
        elif "uncertain" in code.lower() or "±" in code:
            execution_result["output"] = "Result: 15.8 ± 0.4"
            execution_result["type"] = "uncertainty"
        elif "parallel" in code.lower():
            execution_result["output"] = "Parallel execution completed\nTasks: 4, Time: 0.08s"
            execution_result["type"] = "parallel"
        else:
            execution_result["output"] = "30"  # Default numeric result

        if self.current_project:
            self.current_project.execution_results.append(execution_result)

        return execution_result

    def handle_action(self, action_id: str, component_id: str = "", data: Any = None) -> Dict[str, Any]:
        """Handle UI actions"""
        if action_id == "navigate_to_editor":
            return {"action": "navigate", "screen": "EDITOR"}

        elif action_id == "navigate_to_examples":
            return {"action": "navigate", "screen": "EXAMPLES"}

        elif action_id == "navigate_to_quantum":
            return {"action": "navigate", "screen": "QUANTUM"}

        elif action_id == "execute_code":
            code = self.editor.content
            result = self.execute_code(code)
            return {"action": "show_result", "result": result}

        elif action_id == "save_project":
            self.save_current_project()
            return {"action": "notify", "message": "Project saved"}

        elif action_id == "load_example":
            if data and "full_code" in data:
                self.editor.content = data["full_code"]
                return {"action": "navigate", "screen": "EDITOR"}

        elif action_id.startswith("insert_") and action_id.endswith("_template"):
            template_type = action_id.replace("insert_", "").replace("_template", "")
            template = self._get_template(template_type)
            self.editor.insert_text(template)
            return {"action": "update_editor", "content": self.editor.content}

        return {"action": "none"}

    def _get_template(self, template_type: str) -> str:
        """Get code template"""
        templates = {
            "quantum": "quantum[2] {\n    H(q0)\n    CNOT(q0, q1)\n    measure(q0, q1)\n}",
            "uncertain": "let value = 10.5 ± 0.3",
            "parallel": "parallel {\n    let a = compute_task_1()\n    let b = compute_task_2()\n}"
        }
        return templates.get(template_type, "")

    def get_app_state(self) -> Dict[str, Any]:
        """Get current app state"""
        return {
            "current_screen": self.ui.current_screen.name,
            "current_project": self.current_project.to_dict() if self.current_project else None,
            "editor_content": self.editor.content,
            "projects_count": len(self.projects),
            "app_config": self.app_config
        }


# Example usage and testing
if __name__ == "__main__":
    print("Synapse Mobile App Framework")
    print("=" * 40)

    # Create mobile app manager
    app_manager = MobileAppManager()

    # Create sample project
    project = app_manager.create_project("Bell State Demo")
    app_manager.editor.content = "quantum[2] {\n    H(q0)\n    CNOT(q0, q1)\n    measure(q0, q1)\n}"

    print(f"Created project: {project.name}")
    print(f"Project ID: {project.id}")

    # Test code execution
    print("\n--- Code Execution Test ---")
    result = app_manager.execute_code(app_manager.editor.content)
    print(f"Output: {result['output']}")
    print(f"Status: {result['status']}")
    print(f"Execution time: {result['execution_time']}s")

    # Test UI actions
    print("\n--- UI Actions Test ---")
    actions = [
        "navigate_to_editor",
        "execute_code",
        "save_project",
        "insert_quantum_template"
    ]

    for action in actions:
        response = app_manager.handle_action(action)
        print(f"Action '{action}': {response['action']}")

    # Show app configuration
    print("\n--- App Configuration ---")
    app_state = app_manager.get_app_state()
    print(f"Current screen: {app_state['current_screen']}")
    print(f"Projects: {app_state['projects_count']}")
    print(f"App name: {app_state['app_config']['name']}")
    print(f"App version: {app_state['app_config']['version']}")

    # Show examples
    print("\n--- Available Examples ---")
    examples = SynapseExamples.get_examples()
    for category, example_list in examples.items():
        print(f"\n{category}:")
        for example in example_list:
            print(f"  • {example['title']} ({example['difficulty']})")
            print(f"    {example['description']}")

    # Show screen structure
    print("\n--- App Screens ---")
    for screen_name, screen_data in app_state['app_config']['screens'].items():
        children_count = len(screen_data.get('children', []))
        print(f"• {screen_name}: {children_count} components")

    print("\n✅ Mobile app framework implemented!")