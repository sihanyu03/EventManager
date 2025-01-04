def hamming_distance(a: str, b: str):
    if len(a) == len(b):
        return sum(c1 != c2 for c1, c2 in zip(a, b))
    return float('inf')


def check_sql_variable_validity(variable: str):
    return all(c.isalnum() or c == '_' for c in variable)

