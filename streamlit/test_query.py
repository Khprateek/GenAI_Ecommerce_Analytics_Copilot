import sys
import os

sys.path.append(os.path.dirname(__file__))
from utils.bq_client import run_query
from utils.queries import METRICS

q = f"""
SELECT MAX(order_date) as max_date, MIN(order_date) as min_date 
FROM {METRICS}.revenue_daily
"""
print("Min/Max dates:", run_query(q))

q2 = f"""
SELECT order_year, order_month, COUNT(*) 
FROM {METRICS}.revenue_daily 
GROUP BY 1, 2 
ORDER BY 1 DESC, 2 DESC 
LIMIT 5
"""
print("Recent months:", run_query(q2))
