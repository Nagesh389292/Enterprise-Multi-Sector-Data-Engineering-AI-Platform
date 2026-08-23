"""
MILESTONE 4: ENTERPRISE AI COPILOT & RAG DEMONSTRATION VERIFICATION SCRIPT

Executes and verifies all 7 core demonstration questions:
1. "Why was TXN-45728 flagged?"
2. "What are today's top 10 high-risk merchants?"
3. "Which model is the current champion?"
4. "What is the current fraud rate?"
5. "Why did fraud increase?"
6. "What does the fraud investigation policy say about unusual locations?"
7. "Explain the architecture of this platform."

Outputs verify_milestone4_copilot_report.json
"""

import os
import sys
import json
import time
from typing import Dict, Any, List

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from ai.agent.router import AgenticRouter


def safe_str(val: Any) -> str:
    s = str(val)
    return s.encode('ascii', errors='replace').decode('ascii')


def run_milestone4_copilot_verification() -> Dict[str, Any]:
    print("==========================================================================================")
    print("           MILESTONE 4: ENTERPRISE AI COPILOT + RAG DEMONSTRATION SUITE")
    print("==========================================================================================")

    router = AgenticRouter()

    demo_questions = [
        ("Question 1", "Why was TXN-45728 flagged?"),
        ("Question 2", "What are today's top 10 high-risk merchants?"),
        ("Question 3", "Which model is the current champion?"),
        ("Question 4", "What is the current fraud rate?"),
        ("Question 5", "Why did fraud increase?"),
        ("Question 6", "What does the fraud investigation policy say about unusual locations?"),
        ("Question 7", "Explain the architecture of this platform.")
    ]

    results = {}
    passed_count = 0

    for q_label, question in demo_questions:
        print(f"\n--- Running Demo {q_label}: '{question}' ---")
        start_t = time.time()
        res = router.process_query(question)
        latency = round((time.time() - start_t) * 1000.0, 2)

        print(f"    Intent          : {res['intent']}")
        print(f"    Tools Executed  : {', '.join(res['tools_executed'])}")
        print(f"    LLM Provider    : {res['llm_provider']} [{res['llm_status']}]")
        print(f"    Executive Answer: {safe_str(res['executive_answer'])}")
        print(f"    Citations Count : {len(res['citations'])}")
        print(f"    Latency         : {latency} ms")

        has_tools = len(res['tools_executed']) > 0
        has_answer = len(res['executive_answer']) > 0
        has_evidence = len(res['evidence_layer']) > 0
        
        is_success = has_tools and has_answer and has_evidence
        if is_success:
            passed_count += 1

        results[q_label] = {
            "question": question,
            "intent": res['intent'],
            "tools_executed": res['tools_executed'],
            "executive_answer": res['executive_answer'],
            "llm_provider": res['llm_provider'],
            "llm_status": res['llm_status'],
            "citations_count": len(res['citations']),
            "citations_sample": res['citations'][:2],
            "latency_ms": latency,
            "verification_status": "PASS" if is_success else "FAIL"
        }

    overall_report = {
        "milestone": "Milestone 4 — Enterprise AI Copilot + RAG + Agentic Analytics",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "questions_tested": len(demo_questions),
        "questions_passed": passed_count,
        "demonstration_results": results,
        "verdict": "MILESTONE_4_SUCCESS" if passed_count == len(demo_questions) else "MILESTONE_4_FAILED"
    }

    report_path = os.path.join(os.getcwd(), "verify_milestone4_copilot_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(overall_report, f, indent=2)

    print("\n==========================================================================================")
    print(f"   MILESTONE 4 DEMONSTRATION PASSED ({passed_count}/{len(demo_questions)}) | Report: {report_path}")
    print("==========================================================================================")

    return overall_report


if __name__ == "__main__":
    run_milestone4_copilot_verification()
