import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.workflows.healthcare_flow import healthcare_workflow
from src.observability.tracker import tracker

def main():
    print("=" * 75)
    print("  HEALTHCARE MULTI-AGENT PLATFORM (GOOGLE ADK ARCHITECTURE)")
    print("=" * 75)

    query = "Patient John (SSN: 000-12-3456) has acute severe chest pain radiating to left arm."
    print(f"Executing query: '{query}'")
    state = healthcare_workflow.run(user_query=query, patient_id="PT-1001")

    print("\n[Guardrail Detections]:")
    for flag in state.guardrail_flags:
        status = "PASSED" if flag["passed"] else "FLAGGED"
        print(f"  * {flag['guardrail']}: {status}")

    print("\n[Agent Reasoning Trace]:")
    for m in state.messages:
        print(f"  [{m.sender}]: {m.content[:100]}...")

    print(f"\n[Human Review Needed]: {state.needs_human_approval}")
    print("\n[Final Output]:\n", state.final_response)

    print("\n[Platform Telemetry]:", tracker.get_summary())

if __name__ == "__main__":
    main()
