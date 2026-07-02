FORBIDDEN = [
    "DROP",
    "DELETE",
    "UPDATE",
    "INSERT",
    "ALTER",
    "TRUNCATE",
    "MERGE",
    "CREATE"
]


class SQLValidator:

    @staticmethod
    def validate(sql):

        sql_upper = sql.upper()

        if not sql_upper.startswith(("SELECT", "WITH")):
            return False, "Only SELECT statements are allowed."

        for word in FORBIDDEN:

            if word in sql_upper:
                return False, f"{word} is not permitted."

        if ";" in sql[:-1]:
            return False, "Multiple statements detected."

        return True, ""