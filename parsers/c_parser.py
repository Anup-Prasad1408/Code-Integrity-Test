"""Tree-sitter C parser adapter."""
def parse_source(source_code: str):
    from tree_sitter_language_pack import get_parser
    return get_parser("c").parse(source_code.encode("utf-8"))
