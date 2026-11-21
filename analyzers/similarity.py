from engines.ast_engine import compare_analyses

def compare_sources(source_a: dict, source_b: dict):
    """Compare precomputed AST engine outputs."""
    return compare_analyses(source_a, source_b)
