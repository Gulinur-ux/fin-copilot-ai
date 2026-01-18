import frappe
from fin_copilot.ai.llm_connector import ask_ai_for_sql

def execute_ai_query(user_question):
    """
    Bu funksiya 3 ta ishni qiladi:
    1. AIdan SQL so'raydi.
    2. SQL xavfsiz ekanligini tekshiradi (faqat SELECT).
    3. Bazadan ma'lumotni olib qaytaradi.
    """
    
    # 1-Qadam: SQL olish
    sql_query = ask_ai_for_sql(user_question)
    
    # Agar AI xato qaytargan bo'lsa
    if sql_query.startswith("Xatolik") or sql_query.startswith("Error"):
        return sql_query

    # 2-Qadam: Xavfsizlik tekshiruvi (Safety Check) 🛡️
    # Biz faqat ma'lumot o'qishimiz kerak, o'chirish emas!
    forbidden_words = ["DELETE", "DROP", "UPDATE", "INSERT", "ALTER", "TRUNCATE"]
    
    # SQLni katta harfga o'tkazib tekshiramiz
    upper_sql = sql_query.upper()
    
    for word in forbidden_words:
        if word in upper_sql:
            return f"XAVF ANIQLANDI: AI taqiqlangan buyruq ishlatdi ({word}). So'rov bekor qilindi."

    # 3-Qadam: Ijro (Execution)
    try:
        # as_dict=1 degani - natijani chiroyli lug'at (dictionary) qilib beradi
        data = frappe.db.sql(sql_query, as_dict=True)
        
        return {
            "sql": sql_query, # Debug uchun SQLni ham qaytaramiz
            "result": data
        }
        
    except Exception as e:
        return f"SQL Xatolik: {str(e)} \n Kod: {sql_query}"

# Test qilish uchun
# print(execute_ai_query("Show me total expenses"))