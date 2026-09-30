import ast

from app.repositories.models import CodeStructure


class PythonParser:

    def parse(self, content: str):
        return ast.parse(content)

    def extract_functions(self, tree):
        structures = []

        for node in tree.body:

            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):

                parameters = [
                    argument.arg
                    for argument in node.args.args
                ]

                decorators = [
                    ast.unparse(decorator)
                    for decorator in node.decorator_list
                ]

                structure = CodeStructure(
                    type="async_function"
                    if isinstance(node, ast.AsyncFunctionDef)
                    else "function",
                    name=node.name,
                    parameters=parameters,
                    start_line=node.lineno,
                    end_line=node.end_lineno,
                    docstring=ast.get_docstring(node),
                    decorators=decorators,
                )

                structures.append(structure)

        return structures

    def extract_classes(self, tree):
        structures = []

        for node in ast.walk(tree):

            if isinstance(node, ast.ClassDef):

                decorators = [
                    ast.unparse(decorator)
                    for decorator in node.decorator_list
                ]

                bases = [
                    ast.unparse(base)
                    for base in node.bases
                ]

                structure = CodeStructure(
                    type="class",
                    name=node.name,
                    parameters=bases,
                    start_line=node.lineno,
                    end_line=node.end_lineno,
                    docstring=ast.get_docstring(node),
                    decorators=decorators,
                )

                structures.append(structure)

        return structures

    def extract_methods(self, tree):
        structures = []

        for node in ast.walk(tree):

            if isinstance(node, ast.ClassDef):

                for child in node.body:

                    if isinstance(
                        child,
                        (ast.FunctionDef, ast.AsyncFunctionDef)
                    ):

                        parameters = [
                            argument.arg
                            for argument in child.args.args
                        ]

                        decorators = [
                            ast.unparse(decorator)
                            for decorator in child.decorator_list
                        ]

                        structure = CodeStructure(
                            type="async_method"
                            if isinstance(child, ast.AsyncFunctionDef)
                            else "method",
                            name=child.name,
                            parameters=parameters,
                            start_line=child.lineno,
                            end_line=child.end_lineno,
                            parent=node.name,
                            docstring=ast.get_docstring(child),
                            decorators=decorators,
                        )

                        structures.append(structure)

        return structures

    def extract_imports(self, tree):
        imports = []

        for node in ast.walk(tree):

            if isinstance(node, ast.Import):

                for alias in node.names:
                    imports.append(alias.name)

            elif isinstance(node, ast.ImportFrom):

                for alias in node.names:

                    module = node.module or ""

                    if module:
                        imports.append(
                            f"{module}.{alias.name}"
                        )
                    else:
                        imports.append(alias.name)

        return imports

    def extract_assignments(self, tree):
        assignments = []

        for node in tree.body:

            if isinstance(node, ast.Assign):

                for target in node.targets:

                    if isinstance(target, ast.Name):
                        assignments.append(target.id)

            elif isinstance(node, ast.AnnAssign):

                if isinstance(node.target, ast.Name):
                    assignments.append(node.target.id)

        return assignments