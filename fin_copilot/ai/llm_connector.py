import frappe
import requests
import json
from fin_copilot.ai.schema_extractor import get_financial_schema

# --- SOZLAMALAR ---
# Xavfsizlik uchun bu yerni Site Configga o'tkazish tavsiya etiladi.
# Endi kalitni site_config.json dan olamiz
GROQ_API_KEY = frappe.conf.get("groq_api_key")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

@frappe.whitelist()
def ask_ai_for_sql(user_question):
    """
    AI dan tabiiy til savoli asosida SQL so'rovini oladi.
    Client tomondan chaqirish mumkin: frappe.call('fin_copilot.ai.llm_connector.ask_ai_for_sql', { user_question: '...' })
    """
    if not user_question:
        return "Savol kiritilmadi."

    # 1. Schemani olamiz
    try:
        schema = get_financial_schema()
    except Exception as e:
        frappe.log_error(f"Schema Error: {str(e)}", "FinCopilot AI")
        return f"Schema olishda xatolik yuz berdi."

    # 2. Promptni kuchaytiramiz
    # Muhim: Frappe dagi jadvallar 'tab' prefiksi bilan boshlanadi (masalan: `tabGL Entry`)
    system_prompt = f"""
    You are a SQL expert for MariaDB within the Frappe/ERPNext framework.
    
    CRITICAL RULES:
    1. Output ONLY raw SQL query. No markdown (```sql), no explanations, no comments.
    2. In Frappe/ERPNext, database table names are formed by adding 'tab' prefix to the DocType name for standard tables.
       - 'GL Entry' -> `tabGL Entry`
       - 'Account' -> `tabAccount`
    3. Use the provided Schema below to identify correct column names. Do not hallucinate columns.
    
    Database Schema (JSON):
    {json.dumps(schema, indent=2)}
    
    User Question: {user_question}
    Current Date: {frappe.utils.nowdate()}
    """

    # 3. Request tayyorlash
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.1-8b-instant", # Yangilangan model
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Generate the SQL query."} # User question allaqachon prompt ichida bor
        ],
        "temperature": 0.1, # Aniq javob uchun past harorat
        "max_tokens": 1000
    }

    # 4. Yuborish va Tekshirish
    try:
        # print(f"--- Groqqa so'rov yuborilyapti... ---")
        response = requests.post(GROQ_URL, json=payload, headers=headers, timeout=30)
        
        if response.status_code != 200:
            error_msg = f"API Error ({response.status_code}): {response.text}"
            frappe.log_error(error_msg, "FinCopilot AI Groq Error")
            return f"AI xizmatida xatolik: {response.status_code}"
            
        result = response.json()
        
        if 'choices' in result and len(result['choices']) > 0:
            sql = result['choices'][0]['message']['content']
            # Javobni tozalash (ba'zan model baribir markdown qo'shadi)
            clean_sql = sql.replace("```sql", "").replace("```", "").strip()
            return clean_sql
        else:
            return "AI javob qaytarmadi."

    except Exception as e:
        frappe.log_error(f"System Error: {str(e)}", "FinCopilot AI Exception")
        return f"Tizim xatoligi: {str(e)}"