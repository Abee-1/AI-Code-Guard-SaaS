from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from database import verify_key_in_db
import json

app = FastAPI(title="AI Code Guard SaaS Engine", version="2.4.0")

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def verify_client_token(api_key: str = Depends(api_key_header)):
    if not api_key or not verify_key_in_db(api_key):
        raise HTTPException(status_code=403, detail="Access Denied: Invalid Database Token.")
    return api_key

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.0)

class CodeSubmission(BaseModel):
    code: str

SAST_PROMPT = """
You are an expert enterprise static code analyzer and security auditor.
Analyze the provided source code thoroughly for security flaws, configuration weaknesses, or injection vulnerabilities.

You MUST respond strictly in the following JSON format layout, with no extra conversational markdown text outside the JSON structure:
{{
    "vulnerability_found": true,
    "vulnerability_type": "Name of flaw (e.g., Command Injection, Hardcoded Credentials)",
    "severity": "CRITICAL / HIGH / MEDIUM / LOW",
    "target_function": "name_of_vulnerable_function_or_block",
    "line_reference": "Approximate line number or snippet reference",
    "explanation": "Detailed engineering explanation of how the flaw manifests.",
    "remediation": "Step-by-step guidance on how to fix the flaw securely.",
    "secure_code_patch": "Complete, production-ready corrected version of the code snippet."
}}

If the code is clean and contains no identifiable security risks, return:
{{
    "vulnerability_found": false,
    "vulnerability_type": "None",
    "severity": "None",
    "target_function": "None",
    "line_reference": "None",
    "explanation": "Code matches secure best practices.",
    "remediation": "No remediation required.",
    "secure_code_patch": ""
}}
"""

@app.post("/scan")
async def scan_code(submission: CodeSubmission, token: str = Depends(verify_client_token)):
    try:
        sast_chain = ChatPromptTemplate.from_messages([
            ("system", SAST_PROMPT),
            ("user", "Analyze this source code:\n\n{target_code}")
        ]) | llm
        
        raw_response = sast_chain.invoke({"target_code": submission.code}).content.strip()
        
        # Robust cleanup to strip away any markdown wrappers Gemini might add
        clean_json_str = raw_response
        if clean_json_str.startswith("```"):
            clean_json_str = clean_json_str.split("\n", 1)[1]
        if clean_json_str.endswith("```"):
            clean_json_str = clean_json_str.rsplit("\n", 1)[0]
        clean_json_str = clean_json_str.strip()
        
        report = json.loads(clean_json_str)
        return {"status": "success", "analysis": report}
        
    except json.JSONDecodeError:
        # If it still fails, let's look at what raw text caused the issue
        raise HTTPException(status_code=500, detail=f"Failed to parse JSON. Raw output was: {raw_response[:200]}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
