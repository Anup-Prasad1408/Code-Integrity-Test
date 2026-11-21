"""C language parser adapter.

Uses tree-sitter-language-pack when installed. The AST engine also has a
conservative lexical fallback so the application remains usable offline.
"""
def parse_source(source_code: str):
    from tree_sitter_language_pack import get_parser
    parser = get_parser("c")
    return parser.parse(source_code.encode("utf-8"))
