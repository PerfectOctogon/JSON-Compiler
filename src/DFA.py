class DFA:
    """
    A class implementing a Deterministic Finite Automaton (DFA) for lexical analysis
    of JSON-like input strings. The DFA reads the input, identifies tokens, and
    validates their types for use in further syntax analysis.

    Attributes:
        state (str): The current state of the DFA.
        tokens (list): A list of identified tokens from the input.
        token_types (list): A list containing the types of tokens, used for syntax analysis.
        current_token (str): The current token being read by the DFA.
    """
    state = ""
    tokens = []
    # For storing the type of the token only, to be used for syntax analysis
    token_types = []
    current_token = ""

    def __init__(self):
        """
        Initializes the DFA in its start state with empty tokens and token types lists.
        """
        state = "S0"
        self.token_types = []
        self.tokens = []

    # This method tokenizes the input, and then it can be further refined using the DFA
    def tokenize(self, json_input):
        """
        Processes the input string to tokenize JSON-like structures, identifying each token and its type.
        Recognized token types include brackets, braces, colon, comma, strings, numbers, booleans, and nulls.

        Args:
            json_input (str): The input string to be tokenized.

        Returns:
            list: A list of tokens identified from the input.

        Raises:
            ValueError: If an invalid character, unterminated string, or invalid number format is encountered.
        """
        state = "S0"
        current_token = ""
        i = 0

        while i < len(json_input):
            char = json_input[i]

            if state == "S0":
                # Handle different token types from the start state
                if char == '{':
                    self.tokens.append("LBRACE")
                    self.token_types.append("LBRACE")
                elif char == '}':
                    self.tokens.append("RBRACE")
                    self.token_types.append("RBRACE")
                elif char == '[':
                    self.tokens.append("LBRACKET")
                    self.token_types.append("LBRACKET")
                elif char == ']':
                    self.tokens.append("RBRACKET")
                    self.token_types.append("RBRACKET")
                elif char == ':':
                    self.tokens.append("COLON")
                    self.token_types.append("COLON")
                elif char == ',':
                    self.tokens.append("COMMA")
                    self.token_types.append("COMMA")
                elif char == '"':
                    self.token_types.append("STRING")
                    state = "STRING"
                    current_token = ""
                elif char.isdigit() or char == '-':
                    self.token_types.append("NUMBER")
                    state = "NUMBER"
                    current_token = char
                elif char in 'tfn':  # Start of true, false, or null
                    self.token_types.append("KEYWORD")
                    state = "KEYWORD"
                    current_token = char
                elif char.isspace():
                    # Ignore whitespace and stay in S0
                    pass
                else:
                    raise ValueError(f"Unexpected character at position {i}: {char}")

            elif state == "STRING":
                # String reading state
                if char == '"':
                    self.tokens.append(f'STRING:{current_token}')
                    state = "S0"
                elif char == '\\':
                    # Handle escaped characters like \"
                    i += 1
                    if i < len(json_input):
                        current_token += json_input[i]
                    else:
                        raise ValueError("Unexpected end of input in string")
                else:
                    current_token += char

            elif state == "NUMBER":
                # Number reading state
                if char.isdigit() or char in ".eE+-":
                    current_token += char
                else:
                    # Validate if the number is in a proper format
                    try:
                        float(current_token)  # Validate the number
                        self.tokens.append(f'NUMBER:{current_token}')
                    except ValueError:
                        raise ValueError(f"Invalid number at position {i}: {current_token}")
                    state = "S0"
                    i -= 1  # Re-evaluate the current character in the next iteration

            elif state == "KEYWORD":
                # Boolean or null state
                current_token += char
                if current_token in {"true", "false", "null"}:
                    if current_token == "true" or current_token == "false":
                        self.tokens.append(f'BOOL:{current_token.upper()}')
                    else:
                        self.tokens.append("NULL")
                    state = "S0"
                elif not any(k.startswith(current_token) for k in {"true", "false", "null"}):
                    raise ValueError(f"Invalid token at position {i}: {current_token}")

            i += 1

        # Handle end of input and incomplete tokens
        if state == "NUMBER":
            try:
                float(current_token)
                self.tokens.append(f'NUMBER:{current_token}')
            except ValueError:
                raise ValueError(f"Invalid number at end of input: {current_token}")
        elif state == "STRING":
            raise ValueError("Unterminated string literal")
        elif state == "KEYWORD" and current_token not in {"true", "false", "null"}:
            raise ValueError(f"Invalid keyword at end of input: {current_token}")

        return self.tokens
