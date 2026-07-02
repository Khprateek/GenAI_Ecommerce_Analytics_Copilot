from ai.ai_sql_generator import SQLGenerator

generator = SQLGenerator()
client = SQLGenerator()

question = "Show monthly revenue for 2025"

sql = generator.generate(question)
print(sql)