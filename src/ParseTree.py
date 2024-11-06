import DFA


class Node:
    """
    Represents a node in a parse tree.

    Attributes:
        label (str): The label or value of the node.
        is_leaf (bool): True if the node is a leaf, otherwise False.
        parent (Node): The parent node of this node.
        children (list): List of child nodes.
    """
    def __init__(self, label, is_leaf, parent):
        """
        Initializes a Node instance.

        Args:
            label (str): The label or value of the node.
            is_leaf (bool): Indicates if the node is a leaf (True) or not (False).
            parent (Node): The parent node.
        """
        self.label = label
        self.children = []
        self.is_leaf = is_leaf
        self.parent = parent

    def add_child(self, child):
        """
        Adds a child node to this node.

        Args:
            child (Node): The child node to be added.
        """
        self.children.append(child)

    def pre_order_traversal_print(self, depth=0):
        """
        Performs a pre-order traversal, printing each node with indentation.

        Args:
            depth (int): The depth level for indentation (default: 0).
        """
        # Print the current node with distinction for leaf nodes
        prefix = "- Leaf: " if self.is_leaf else "- Node: "
        print(" " * (depth * 2) + f"{prefix}{self.label}")

        # Traverse each child in pre-order
        for child in self.children:
            child.pre_order_traversal_print(depth + 1)

    def pre_order_traversal_output(self, depth=0, file=None):
        """
        Performs a pre-order traversal, writing each node to the specified file.

        Args:
            depth (int): The depth level for indentation (default: 0).
            file (TextIO): The file to write the output to.
        """
        # Define prefix based on whether the node is a leaf
        prefix = "- Leaf: " if self.is_leaf else "- Node: "
        line = " " * (depth * 2) + f"{prefix}{self.label}\n"

        # Write the line to the file
        if file:
            file.write(line)
        else:
            print(line, end='')  # Fallback to console output if no file is provided

        # Traverse each child in pre-order
        for child in self.children:
            child.pre_order_traversal_output(depth=depth + 1, file=file)

class ParseTree:
    """
    Represents a parse tree for JSON-like structures, utilizing a DFA lexer for tokenization.

    Attributes:
        lexer (DFA): The DFA lexer instance used to tokenize input.
        current_token_index (int): Index of the current token being parsed.
        current_token (str): The current token type.
        parent_node (Node): The root node of the parse tree.
    """
    def __init__(self, lexer):
        """
        Initializes the ParseTree instance with a lexer.

        Args:
            lexer (DFA): An instance of the DFA lexer for tokenizing input.
        """
        self.lexer = lexer
        self.current_token_index = 1
        self.current_token = self.lexer.token_types[self.current_token_index - 1]
        self.parent_node = None

    def set_parent_node(self, node):
        """
        Sets the parent node for the parse tree.

        Args:
            node (Node): The root node of the parse tree.
        """
        self.parent_node = node

    def get_next_token(self):
        """
        Advances to the next token in the lexer token stream.

        Raises:
            Exception: If no valid end of file token is found.
        """
        try:
            self.current_token = self.lexer.token_types[self.current_token_index]
            self.current_token_index += 1
        except Exception as e:
            raise Exception("Missing end of file token (RBRACE / RBRACKET)")

    def parse_list(self, token_passed, parent_node):
        """
        Parses a JSON list structure and builds a corresponding subtree.

        Args:
            token_passed (str): The current token type.
            parent_node (Node): The parent node for this list in the parse tree.

        Returns:
            bool: True if parsing is successful.

        Raises:
            Exception: If an unexpected token is encountered or the list ends improperly.
        """
        # Configure node of parse tree
        node = Node("list", False, parent_node)
        parent_node.add_child(node)
        node.add_child(Node("[", True, node))

        if token_passed == "RBRACKET":
            try:
                node.add_child(Node("]", True, node))
                self.get_next_token()
            except Exception as e:
                print("End of file")
            return True

        while token_passed in ["STRING", "NUMBER", "KEYWORD", "LBRACKET", "LBRACE"]:
            if token_passed == "LBRACKET":
                self.get_next_token()
                token_passed = self.current_token
                self.parse_list(token_passed, node)

            elif token_passed == "LBRACE":
                self.get_next_token()
                token_passed = self.current_token
                self.parse_dict(token_passed, node)

            else:
                self.get_next_token()
                node.add_child(Node(token_passed, True, node))

            token_passed = self.current_token

            if token_passed == "COMMA":
                node.add_child(Node(",", True, node))
                self.get_next_token()
                if self.current_token == "RBRACKET":
                    raise Exception(f"Comma before end of list at token number {self.current_token_index}")
            elif token_passed == "RBRACKET":
                try:
                    node.add_child(Node("]", True, node))
                    self.get_next_token()
                except Exception as e:
                    print("End of file")
                return True
            else:
                raise Exception(f"Unknown token in list {token_passed} at token number {self.current_token_index}")
            token_passed = self.current_token

        if token_passed == "RBRACKET":
            return True
        else:
            raise Exception(f"Unknown value in list {token_passed}")

    def parse_dict(self, token_passed, parent_node):
        """
        Parses a JSON dictionary structure and builds a corresponding subtree.

        Args:
            token_passed (str): The current token type.
            parent_node (Node): The parent node for this dictionary in the parse tree.

        Returns:
            bool: True if parsing is successful.

        Raises:
            Exception: If an unexpected token is encountered or the dictionary ends improperly.
        """
        # configuring new node for parse tree
        node = Node("dict", False, parent_node)
        parent_node.add_child(node)
        node.add_child(Node("{", True, node))

        if token_passed == "RBRACE":
            try:
                node.add_child(Node("}", True, node))
                self.get_next_token()
            except Exception as e:
                print("End of file")
            return True  # End of dictionary

        # Process pairs of STRING (key) and values separated by a colon
        while token_passed == "STRING":
            # Expect a key (STRING), so move to the next token
            self.get_next_token()
            node.add_child(Node("STRING", True, node))

            # Expect a colon after the key
            if self.current_token != "COLON":
                raise Exception(f"Expected COLON after key in dict, found {self.current_token}")
            self.get_next_token()
            node.add_child(Node(":", True, node))

            # Process the value associated with the key
            token_passed = self.current_token
            if token_passed in ["STRING", "NUMBER", "KEYWORD", "LBRACKET", "LBRACE"]:
                if token_passed == "LBRACKET":
                    self.get_next_token()
                    token_passed = self.current_token
                    self.parse_list(token_passed, node)
                elif token_passed == "LBRACE":
                    self.get_next_token()
                    token_passed = self.current_token
                    self.parse_dict(token_passed, node)
                else:
                    self.get_next_token()
                    node.add_child(Node(token_passed, True, node))
            else:
                raise Exception(f"Unexpected value type {token_passed} in dict")

            # Check for a comma or closing brace after each pair
            token_passed = self.current_token
            if token_passed == "COMMA":
                self.get_next_token()
                node.add_child(Node(",", True, node))
                token_passed = self.current_token
                if token_passed == "RBRACE":
                    raise Exception(f"Comma before end of dictionary at token number {self.current_token_index}")
            elif token_passed == "RBRACE":
                try:
                    node.add_child(Node("}", True, node))
                    self.get_next_token()
                except Exception as e:
                    print("End of file")
                return True  # End of dictionary
            else:
                raise Exception(f"Unexpected token {token_passed} in dict at token number {self.current_token_index}")
        else:
            raise Exception(f"Unknown token in dict {token_passed} at token number {self.current_token_index}")

    def parse(self):
        """
        Parses the JSON-like input based on the starting token and builds the parse tree.

        Raises:
            Exception: If the input starts incorrectly or there are unexpected tokens at the end.
        """
        if self.current_token in ["LBRACE"]:
            self.parent_node = Node("StartOfParseTree", False, None)
            self.get_next_token()
            self.parse_dict(self.current_token, self.parent_node)

        elif self.current_token in ["LBRACKET"]:
            self.parent_node = Node("StartOfParseTree", False, None)
            self.get_next_token()
            self.parse_list(self.current_token, self.parent_node)

        else:
            raise Exception(f"Illegal start of file {self.current_token}")

        if self.current_token_index < len(self.lexer.token_types):
            raise Exception(f"Unexpected tokens at end of file")
