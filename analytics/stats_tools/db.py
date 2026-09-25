from __future__ import annotations

from typing import Any, Optional

import pandas as pd
from django.db import connections

# Alias of a Django DATABASES entry pointed at the same MySQL instance but
# with a DB user that only has SELECT grants. Configure in settings.py:
#   DATABASES = {"default": {...}, "analytics_readonly": {...same host, readonly user...}}
_DB_ALIAS = "analytics_readonly"
_MAX_ROWS = 10_000

# Tables the NL2SQL path (get_schema / run_query) is allowed to touch.
# This is a convenience allowlist for get_schema's listing — the actual
# security boundary is the analytics_readonly MySQL user's GRANTs, which
# should be scoped to exactly these tables (never GRANT SELECT ON *.*).
_ALLOWED_TABLES = {
    "zone_zone",
    "visit_visit",
    "response_response",
    "question_question",
    "surveysession_surveysession",
    "option_option",
    "flat_responses"
}


def _fetch(sql: str, params: Optional[list] = None) -> pd.DataFrame:
    """Run a query on the read-only alias and return a DataFrame. Internal helper."""
    with connections[_DB_ALIAS].cursor() as cursor:
        cursor.execute(sql, params or [])
        columns = [c[0] for c in cursor.description]
        rows = cursor.fetchall()
    return pd.DataFrame(rows, columns=columns)


def get_schema(table: Optional[str] = None) -> str:
    """
    Return the schema as a DDL string (CREATE TABLE statements, via MySQL's
    own SHOW CREATE TABLE) plus a foreign-key relationship listing, for the
    tables the agent may query. This is meant to be embedded directly into
    the LLM's context — a plain string the model can read like it would
    read any SQL DDL, not a JSON structure it has to interpret. Call this
    before run_query whenever you're not already certain of the exact
    table/column names or how tables relate to each other.

    Restricted to _ALLOWED_TABLES: the `table` argument (if the LLM
    supplies one) is validated against that allowlist before being
    interpolated into SHOW CREATE TABLE, so this never runs DDL inspection
    against a table outside the agent's intended scope.
    """
    tables = [table] if table else sorted(_ALLOWED_TABLES)
    if table and table not in _ALLOWED_TABLES:
        return (
            f"-- '{table}' is not an accessible table.\n"
            f"-- Accessible tables: {', '.join(sorted(_ALLOWED_TABLES))}"
        )

    ddl_blocks: list[str] = []
    with connections[_DB_ALIAS].cursor() as cursor:
        for t in tables:
            # t only ever comes from _ALLOWED_TABLES (validated above, or
            # the hardcoded default list) — never raw, unvalidated input —
            # so interpolating it into SHOW CREATE TABLE is safe.
            cursor.execute(f"SHOW CREATE TABLE `{t}`")
            row = cursor.fetchone()
            if row:
                ddl_blocks.append(row[1].strip() + ";")

        cursor.execute(
            "SELECT table_name, column_name, referenced_table_name, referenced_column_name "
            "FROM information_schema.key_column_usage "
            "WHERE table_schema = DATABASE() AND referenced_table_name IS NOT NULL "
            "AND table_name IN %s",
            [tuple(tables)],
        )
        foreign_keys = cursor.fetchall()

    schema_str = "\n\n".join(ddl_blocks)

    if foreign_keys:
        fk_lines = "\n".join(
            f"-- {tbl}.{col} -> {ref_table}.{ref_col}"
            for tbl, col, ref_table, ref_col in foreign_keys
        )
        schema_str += f"\n\n-- Foreign key relationships:\n{fk_lines}"

    return schema_str


def run_query(sql: str, params: Optional[list] = None) -> dict:
    """
    Execute a read-only SELECT against the database and return rows as records.

    Safety:
      - only SELECT/WITH statements are allowed (naive but effective first gate;
        pair this with the readonly DB user, which has no write/DDL grants —
        never rely on string checks alone).
      - always pass `params` positionally (%s placeholders), never
        string-format user input into `sql`.
      - result is capped at _MAX_ROWS to keep the LLM's context bounded.
    """
    stripped = sql.strip().lower()
    if not (stripped.startswith("select") or stripped.startswith("with")):
        return {"error": "Only SELECT/WITH statements are permitted."}

    df = _fetch(sql, params)

    truncated = len(df) > _MAX_ROWS
    if truncated:
        df = df.head(_MAX_ROWS)

    

    return df.to_csv(index=False)


TOOL_SCHEMAS = [
    {
        "name": "get_schema",
        "description": "Return the DDL (CREATE TABLE statements) and foreign key relationships for the accessible tables (zones, visits, questions, survey sessions, options, flat_responses), as a plain SQL-formatted string. Call this before run_query if you're not certain of exact table/column names or how tables relate.",
        "input_schema": {
            "type": "object",
            "properties": {
                "table": {
                    "type": "string",
                    "description": "Omit to list all accessible tables.",
                }
            },
        },
    },
    {
        "name": "run_query",
        "description": (
            "Run a read-only, exploratory SELECT query against the MySQL database "
            "for descriptive/lookup questions (counts, listings, filters) that "
            "don't need get_flat_responses. Check get_schema first if unsure of "
            "column names. Do NOT use this for hypothesis-testing analysis — use "
            "get_flat_responses + pivot_responses for that instead."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "sql": {
                    "type": "string",
                    "description": "A SELECT/WITH statement. Use %s placeholders, never string-format values in.",
                },
                "params": {
                    "type": "array",
                    "description": "Positional parameters for %s placeholders in sql.",
                    "items": {},
                },
            },
            "required": ["sql"],
        },
    },
    
]


TOOL_DISPATCH = {
    "get_schema": get_schema,
    "run_query": run_query,
    # "get_flat_responses": get_flat_responses,
    # "pivot_responses": pivot_responses,
    # "get_visit_pivot": get_visit_pivot,
    # "get_descriptive_stats": get_descriptive_stats,
    # "recommend_test": recommend_test,
    # "run_statistical_test": run_statistical_test,
    # "generate_plot": generate_plot,
}
