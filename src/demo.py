import ast

code = """
x = 1

def func():
    print("This is a function")

class MyClass:
    def method(self):
        print("This is a method")
"""

class NodeVisitor(ast.NodeVisitor):
    def __init__(self):
        self.nodes = []

    def visit_FunctionDef(self, node):
        if not any(isinstance(parent, ast.ClassDef) for parent in self.parents):
            self.nodes.append((node, 'Function'))
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.nodes.append((node, 'Class'))
        self.parents.append(node)
        self.generic_visit(node)
        self.parents.pop()

    def visit_Assign(self, node):
        self.nodes.append((node, 'Assign'))
        self.generic_visit(node)

tree = ast.parse(code)
visitor = NodeVisitor()
visitor.parents = []
visitor.visit(tree)

# Sort the nodes by their line number
visitor.nodes.sort(key=lambda node: node[0].lineno)

for i in range(len(visitor.nodes)):
    node, node_type = visitor.nodes[i]
    start_line = node.lineno
    if i < len(visitor.nodes) - 1:
        end_line = visitor.nodes[i+1][0].lineno
    else:
        end_line = len(code.splitlines()) + 1
    node_code = "\n".join(code.splitlines()[start_line-1:end_line-1])
    print(f"Code for {node_type} at line {start_line}:\n{node_code}\n")
