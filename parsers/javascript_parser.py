"""Tree-sitter JavaScript parser adapter."""
def parse_source(source_code: str):
    from tree_sitter_language_pack import get_parser
    return get_parser("javascript").parse(source_code.encode("utf-8"))
