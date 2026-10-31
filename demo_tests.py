"""Offline deterministic tests; does not claim to measure live LLM answer accuracy."""
import json, time
from agent import (tool_fee_status, tool_scholarship_status, tool_exam_schedule,
                   tool_timetable, tool_calendar, retrieve_policy, save_memory,
                   load_memory, TRACE_PATH)

CASES = [
    ("1. Current fee status for S1004", lambda: tool_fee_status("S1004"), "pending"),
    ("2. Portal failure policy", lambda: retrieve_policy("payment portal failed next working day fee due date"), "Fee payment and portal downtime"),
    ("3. New session recalls saved preferred name", lambda: (save_memory("session-restart-demo","preferred_name","Mahi"), load_memory("session-restart-demo")), "Mahi"),
    ("4. Sensitive temporary information is not persisted", lambda: save_memory("privacy-demo","medical_note","temporary health detail"), "not eligible"),
    ("5. Unsupported policy question returns no retrieved evidence", lambda: retrieve_policy("swimming pool opening hours"), "empty"),
    ("Semester I exam tool", lambda: tool_exam_schedule("semester 1"), "exams"),
    ("Semester II timetable tool", lambda: tool_timetable("semester 2","monday"), "classes"),
    ("Academic calendar tool", lambda: tool_calendar("2026-11-01","2026-11-30"), "events"),
    ("Scholarship tool", lambda: tool_scholarship_status("S1004"), "under review"),
]
results=[]
for name, fn, expected in CASES:
    start=time.perf_counter()
    try:
        value=fn()
        rendered=json.dumps(value,ensure_ascii=False).lower()
        passed = (value == []) if expected=="empty" else expected.lower() in rendered
        results.append({"test":name,"passed":passed,"latency_seconds":round(time.perf_counter()-start,4),
                        "evidence":str(value)[:350]})
    except Exception as exc:
        results.append({"test":name,"passed":False,"latency_seconds":round(time.perf_counter()-start,4),
                        "evidence":f"{type(exc).__name__}: {exc}"})
print("\\nDETERMINISTIC TOOL / RETRIEVAL TEST REPORT")
print(json.dumps(results,indent=2,ensure_ascii=False))
passed=sum(r["passed"] for r in results)
print(f"\\nComponent test accuracy: {passed/len(results):.1%} ({passed}/{len(results)})")
print("This is not end-to-end LLM answer accuracy. Live latency/tokens/tool choices are recorded per query in traces.jsonl.")
print(f"Trace file: {TRACE_PATH}")
