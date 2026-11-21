import ast

def parse_source(source_code: str):
    """Return a native Python AST, or raise SyntaxError for invalid code."""
    return ast.parse(source_code)

def canonical_nodes(tree):
    """AST node labels with identifiers and literal values anonymized."""
    labels = []
    class Visitor(ast.NodeVisitor):
        def generic_visit(self, node):
            if isinstance(node, ast.Name):
                labels.append("Name")
                return
            if isinstance(node, (ast.arg,)):
                labels.append("arg")
                return
            if isinstance(node, (ast.Constant,)):
                labels.append("Constant")
                return
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                labels.append(type(node).__name__)
                labels.append("args")
                for child in node.args.args:
                    labels.append("arg")
                for child in node.body:
                    self.visit(child)
                return
            labels.append(type(node).__name__)
            super().generic_visit(node)
    Visitor().visit(tree)
    return labels
