def clean_sql(sql: str):

    sql = sql.replace("```sql", "")

    sql = sql.replace("```", "")

    return sql.strip()