"""JavaScript parser adapter (kept under legacy module name for project continuity)."""
def parse_source(source_code: str):
    from tree_sitter_language_pack import get_parser
    parser = get_parser("javascript")
    return parser.parse(source_code.encode("utf-8"))
