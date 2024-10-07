import os
from typing import Union, List, Optional

alphabet_chars = list("abcdefghijklmnopqrstuvwxyz") + list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
numeric_chars = list("0123456789")
var_chars = alphabet_chars + numeric_chars
all_valid_chars = var_chars + ["(", ")", ".", "\\"]
valid_examples_fp = "./valid_examples.txt"
invalid_examples_fp = "./invalid_examples.txt"
extra_valid_examples_fp = "./extra_valid_examples.txt"
extra_invalid_examples_fp = "./extra_invalid_examples.txt"


def read_lines_from_txt(fp: Union[str, os.PathLike]) -> List[str]:
  """
  :param fp: File path of the .txt file.
  :return: The lines of the file path removing trailing whitespaces
  and newline characters.
  """

  with open(fp, "r") as f:
    raw_lines = f.readlines()

    # remove whitespaces for each line
    lines = [line.strip() for line in raw_lines]

    return lines


def is_valid_var_name(s: str) -> bool:
  """
  :param s: Candidate input variable name
  :return: True if the variable name starts with a character,
  and contains only characters and digits. Returns False otherwise.
  """

  # check var name starts with character
  if s[0] not in alphabet_chars:
    print("")
    return False

  # check rest of var name is only characters and digits
  for x in s[1:]:
    if x not in var_chars:
      return False

  # passed all validity tests
  return True


class Node:
  """
  Nodes in a parse tree
  Attributes:
      elem: a list of strings
      children: a list of child nodes
  """

  def __init__(self, elem: List[str] = None):
    self.elem = elem
    self.children = []

  def add_child_node(self, node: 'Node') -> None:
    self.children.append(node)


class ParseTree:
  """
  A full parse tree, with nodes
  Attributes:
      root: the root of the tree
  """

  def __init__(self, root):
    self.root = root

  def print_tree(self, node: Optional[Node] = None, level: int = 0) -> None:
    # customized to look exactly like example in slides

    # start with root node
    if node is None:
      node = self.root
    # current node
    indent = '----' * level
    # print full tree elem as shown in example
    for token in node.elem:
      print(indent + token)
    # recursive call to print child nodes
    for child in node.children:
      # increase level of indent and tree
      self.print_tree(child, level + 1)


def parse_tokens_rec(s_: str, original: str, pos: int, association_type: Optional[str] = None) -> Union[List[str], bool]:
  """
  Recursive function to accompany parse_tokens()
  Uses a top-down parsing approach to identify all tokens with necessary brackets

  :param s_: the input string
  :param original: original string unmodified to display location of error
  :param pos: current position tracking through recursion to identify location of error
  :param association_type: If not None, add brackets to make expressions non-ambiguous
  :return: A List of tokens (strings) if a valid input, otherwise False
  """

  s = s_[:]  # Don't modify the original input string

  s = s.strip()  # remove trailing whitespaces, if any
  tokens = []  # collect tokens

  # case 0: base case when string is blank
  if len(s) == 0:
    return []

  # case 1: blank space
  if s[0] == " ":
    return parse_tokens_rec(s[1:], original, pos + 1, association_type)
    # END case

  # case 2: variables
  if s[0] == "\\":
    tokens.append(s[0])
    end_index = 1
    while end_index < len(s) and s[end_index] in var_chars:
      end_index += 1
    if end_index == 1:
      # ERROR
      print("Error in [" + original + "] at position " + str(pos + 2) + ": No valid variable name found.")
      return False
    if s[1] not in alphabet_chars:
      # ERROR
      print("Error in [" + original + "] at position " + str(pos + 2) + ": Variable must start with a character.")
      return False
    if end_index + 1 >= len(s):
      # ERROR
      print("Error in [" + original + "] at position " + str(pos + 2) + ": No expression found after variable.")
      return False
    tokens.append(s[1:end_index])
    spaces_len = 0  # keep track of spaces between var and next character
    while end_index < len(s) and s[end_index] == " ":
      spaces_len += 1
      end_index += 1
    # check if dot expression exists
    dot_expr = False
    # dot operation detected
    if s[end_index] == ".":
      # space exists between dot and variable
      if spaces_len > 0:
        # ERROR
        print(
          "Error in [" + original + "] at position " + str(pos + end_index) +
          ": No spaces allowed between variable and dot."
        )
        return False  # no spaces allowed before "." according to invalid examples
      end_index += 1
      dot_expr = True
    # recursive call
    nested_tokens = parse_tokens_rec(s[end_index:], original, pos + end_index, association_type)
    if not nested_tokens:
      return False  # ERROR - message returned further down in recursive calls
    # subcase 2.1: dot operator, only expected after a variable
    add_extra_brackets = True
    # check if brackets already take care of grouping
    if nested_tokens[0] == "(":
      bracket_count = 1  # keep track of brackets
      bracket_index = 1  # to check respective position to string length
      while bracket_index < len(nested_tokens):
        if nested_tokens[bracket_index] == "(":
          bracket_count += 1
        elif nested_tokens[bracket_index] == ")":
          bracket_count -= 1
        if bracket_count == 0:
          # the first bracket being tracked is closed
          break
        bracket_index += 1
      if bracket_index == len(nested_tokens) - 1:
        # do not add extra brackets from dot operator if the following bracket covers the entire string
        add_extra_brackets = False
    # RESOLVE AMBIGUITY: add extra brackets only if necessary for dot expressions
    if dot_expr and add_extra_brackets:
      tokens.append("(")
    # add collected tokens
    tokens.extend(nested_tokens)
    if dot_expr and add_extra_brackets:
      tokens.append(")")
    return tokens
    # END case

  # case 3: brackets
  if s[0] == "(":
    bracket_count = 1
    end_index = 1
    while end_index < len(s) and bracket_count != 0:
      if s[end_index] == "(":
        bracket_count += 1
      if s[end_index] == ")":
        bracket_count -= 1
      end_index += 1
    if bracket_count > 0:
      # ERROR
      error_component = "EOL."
      if end_index < len(s) - 1:
        error_component = s[end_index + 1] + "."
      print(
        "Error in [" + original + "] at position " + str(pos + end_index) +
        ": Expected closing parenthesis, found " + error_component
      )
      return False
    if end_index <= 2:
      # ERROR
      print(
        "Error in [" + original + "] at position " + str(pos + 1) +
        ": Missing tokens between brackets."
      )
      return False
    # recursive call
    nested_tokens = parse_tokens_rec(s[1:end_index - 1], original, pos + 1, association_type)
    if not nested_tokens:
      return False  # ERROR - message returned further down in recursive calls
    # pre-subcase 3.1: bracket does not go up to the end of the string
    if end_index + 1 < len(s) and association_type:
      tokens.append("(")
    # add tokens with brackets
    tokens.append("(")
    tokens.extend(nested_tokens)
    tokens.append(")")
    # subcase 3.1: more expression after bracket ends
    if end_index < len(s):
      # recursive call
      additional_tokens = parse_tokens_rec(s[end_index:], original, pos + end_index, association_type)
      if additional_tokens == False:
        return False  # ERROR - message returned further down in recursive calls
      tokens.extend(additional_tokens)
    if end_index + 1 < len(s) and association_type:
      tokens.append(")")
    return tokens
    # END case

  # case 4: all other characters
  if s[0] in var_chars:
    if s[0] not in alphabet_chars:
      # ERROR
      print("Error in [" + original + "] at position " + str(pos + 1) + ": Name must start with a character.")
      return False
    end_index = 1
    # find length of all characters that are tokens of the expression chain
    while end_index < len(s) and s[end_index] in var_chars + [" "]:
      end_index += 1
    # split into char tokens to add associativity optionally, otherwise extend tokens list directly
    char_tokens = s[:end_index].strip().split(" ")
    if association_type:
      # RESOLVE AMBIGUITY: add association
      char_tokens = add_associativity(char_tokens, association_type)
    tokens.extend(char_tokens)
    # recursive call
    additional_tokens = parse_tokens_rec(s[end_index:], original, pos + end_index, association_type)
    if additional_tokens == False:
      return False  # ERROR - message returned further down in recursive calls
    tokens.extend(additional_tokens)
    return tokens
    # END case

  # case 5: anything else unknown
  else:
    # ERROR
    print("Error in [" + original + "] at position " + str(pos + 1) + ": Unexpected token '" + s[0] + "'")
    return False
    # END case


def parse_tokens(s_: str, association_type: Optional[str] = None) -> Union[List[str], bool]:
  """
  Gets the final tokens for valid strings as a list of strings, only for valid syntax,
  where tokens are (no whitespace included)
  \\ values for lambdas
  valid variable names
  opening and closing parenthesis
  Note that dots are replaced with corresponding parenthesis

  :param s_: the input string
  :param association_type: If not None, add brackets to make expressions non-ambiguous
  :return: A List of tokens (strings) if a valid input, otherwise False
  """
  s = s_[:]
  return parse_tokens_rec(s, s, 0, association_type)


def read_lines_from_txt_check_validity(fp: Union[str, os.PathLike]) -> None:
  """
  Reads each line from a .txt file, and then
  parses each string  to yield a tokenized list of strings for printing, joined by _ characters
  In the case of a non-valid line, the corresponding error message is printed (not necessarily within
  this function, but possibly within the parse_tokens function).
  :param lines: The file path of the lines to parse
  """
  lines = read_lines_from_txt(fp)
  valid_lines = []
  for l in lines:
    tokens = parse_tokens(l)
    if tokens:
      valid_lines.append(l)
      print(f"The tokenized string for input string {l} is {'_'.join(tokens)}")
  if len(valid_lines) == len(lines):
    print(f"All lines are valid")


def read_lines_from_txt_output_parse_tree(fp: Union[str, os.PathLike]) -> None:
  """
  Reads each line from a .txt file, and then
  parses each string to yield a tokenized output string, to be used in constructing a parse tree. The
  parse tree should call print_tree() to print its content to the console.
  In the case of a non-valid line, the corresponding error message is printed (not necessarily within
  this function, but possibly within the parse_tokens function).
  :param fp: The file path of the lines to parse
  """
  lines = read_lines_from_txt(fp)
  for l in lines:
    tokens = parse_tokens(l)
    if tokens:
      print("\n")
      parse_tree2 = build_parse_tree(tokens)
      parse_tree2.print_tree()


def add_associativity(s_: List[str], association_type: str = "left") -> List[str]:
  """
  :param s_: A list of string tokens
  :param association_type: a string in [`left`, `right`]
  :return: List of strings, with added parenthesis that disambiguates the original expression
  """

  s = s_[:]  # Don't modify original string

  if len(s) <= 1:  # base case
    return s
  if association_type == "left":  # ((a b) c)
    group = add_associativity(s[:-1], association_type)
    return ["("] + group + [s[-1]] + [")"]
  elif association_type == "right":  # (a (b c))
    group = add_associativity(s[1:], association_type)
    return ["("] + [s[0]] + group + [")"]
  else:  # invalid type
    print("Warning: unknown association type: " + association_type + " , using default grouping")
    return s


def build_parse_tree_rec(tokens: List[str], node: Optional[Node] = None) -> Node:
  """
  An inner recursive inner function to build a parse tree
  :param tokens: A list of token strings
  :param node: A Node object
  :return: a node with children whose tokens are variables, parenthesis, slashes, or the inner part of an expression
  """

  if node is None:
    node = Node(["_".join(tokens)])  # initial node
  i = 0
  while i < len(tokens):
    token = tokens[i]
    if token == '(':
      # token subtree
      subtree_tokens = []
      node.add_child_node(Node(['(']))
      paren_count = 1
      i += 1
      while i < len(tokens) and paren_count > 0:
        if tokens[i] == '(':
          paren_count += 1
        elif tokens[i] == ')':
          paren_count -= 1
        if paren_count > 0:
          subtree_tokens.append(tokens[i])
        i += 1
      # recursive call
      subtree = build_parse_tree_rec(subtree_tokens)
      node.add_child_node(subtree)
      node.add_child_node(Node([')']))
    elif token == '\\':
      i += 1
      var_token = tokens[i]
      lambda_node = Node([f"\\", var_token])
      node.add_child_node(lambda_node)
      i += 1
    else:
      var_node = Node([token])
      node.add_child_node(var_node)
      i += 1
  return node


def build_parse_tree(tokens: List[str]) -> ParseTree:
  """
  Build a parse tree from a list of tokens
  :param tokens: List of tokens
  :return: parse tree
  """
  pt = ParseTree(build_parse_tree_rec(tokens))
  return pt


if __name__ == "__main__":
  print("\n\nChecking valid examples...")
  read_lines_from_txt_check_validity(valid_examples_fp)
  read_lines_from_txt_output_parse_tree(valid_examples_fp)

  print("\n\nChecking invalid examples...")
  read_lines_from_txt_check_validity(invalid_examples_fp)

  print("\n\nChecking extra valid examples...")
  read_lines_from_txt_check_validity(extra_valid_examples_fp)
  read_lines_from_txt_output_parse_tree(extra_valid_examples_fp)

  print("\n\nChecking extra invalid examples...")
  read_lines_from_txt_check_validity(extra_invalid_examples_fp)

  # Optional
  print("\n\nAssociation Examples:")
  sample = ["a", "b", "c"]
  print("Right association")
  associated_sample_r = add_associativity(sample, association_type="right")
  print(associated_sample_r)
  print("Left association")
  associated_sample_l = add_associativity(sample, association_type="left")
  print(associated_sample_l)

  # Additional tests for asociation - from optional
  print("\n\nAdditional association tests when parsing tokens")
  test_association_left = parse_tokens("\\x.\\y (x y b c)", "left")
  print(test_association_left)
  test_association_right = parse_tokens("\\x.\\y (x y b c)", "right")
  print(test_association_right)
  test_association_right = parse_tokens("\\x.\\y (x y b c)", "asdf")
  print(test_association_right)

  # Additional test for parse tree
  print("\n\nAdditional parse tree test for demo")
  tokens = parse_tokens("\\x.\\y (x y b c)")
  parse_tree2 = build_parse_tree(tokens)
  parse_tree2.print_tree()
