import DFA
import ParseTree

dfa = DFA.DFA()
with open("../res/sampleJSON.txt", "r") as file:
    json_input = file.read()
    file.close()

tokens = dfa.tokenize(json_input)
print(tokens)


def write_token(tokens):
    with open("../output/tokenizedOutput.txt", 'w') as write_file:
        string_to_write = ""
        for token in tokens:
            string_to_write += token + "\n"
        write_file.write(string_to_write)
        write_file.close()


write_token(tokens)

parse_tree = ParseTree.ParseTree(dfa)

print(parse_tree.parse())

parse_tree.parent_node.pre_order_traversal_print()

with open("../output/parsetree.txt", 'w') as file:
    parse_tree.parent_node.pre_order_traversal_output(file=file)
