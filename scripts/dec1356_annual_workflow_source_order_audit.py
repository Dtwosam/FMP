"""DEC-1356: inspect caller-provided annual workflow SOURCE TEXT only.

No workflow is executed, dispatched, installed or edited here. The parser
does not open files, contact GitHub or inspect protected annual evidence.
This diagnostic cannot prove the server-side dispatched workflow identity.
"""
from __future__ import annotations

import re

JOBS=("annual_preflight","annual_cell","annual_freeze")
PERMANENT_BLOCKERS=(
    "INDEPENDENT_PROTECTED_OS_NO_WRITE_NOT_VERIFIED",
    "SERVER_SIDE_EXCLUSIVE_IMMUTABLE_REF_SHA_NOT_VERIFIED",
    "RUN385_ATTEMPT1_SEPARATE_ONE_SHOT_AUTHORITY_NOT_VERIFIED",
)
JOB_LINE=re.compile(r"^  (annual_preflight|annual_cell|annual_freeze):\s*$",
                    re.MULTILINE)
STEP_LINE=re.compile(r"^      - name:\s*(.+?)\s*$",re.MULTILINE)
CELL_LINE=re.compile(r"^          - symbol:\s*",re.MULTILINE)


def audit_annual_workflow_source(source: object) -> dict[str, object]:
    """Always BLOCKED; extract only negative ordering facts from text."""
    problems=list(PERMANENT_BLOCKERS)
    inventory={}
    if type(source) is not str:
        problems.append("WORKFLOW_SOURCE_NOT_TEXT")
    else:
        found=list(JOB_LINE.finditer(source))
        names=[m.group(1) for m in found]
        for required in JOBS:
            if names.count(required)!=1:
                problems.append("REQUIRED_JOB_ABSENT_OR_DUPLICATED_"+required)
        for i,m in enumerate(found):
            name=m.group(1)
            end=found[i+1].start() if i+1<len(found) else len(source)
            content=source[m.start():end]
            steps=tuple(v.group(1).strip() for v in STEP_LINE.finditer(content))
            inventory[name]=steps
            if not steps or steps[0]=="Checkout":
                problems.append("NO_INDEPENDENT_ADMISSION_BEFORE_CHECKOUT_"+name)
            if "refs/heads/main" in content:
                problems.append("MUTABLE_MAIN_ONLY_GATE_"+name)
            install=next((j for j,v in enumerate(steps)
                          if v=="Install pinned annual catalogue runtime"),None)
            auth=next((j for j,v in enumerate(steps)
                       if "authorized annual catalogue execution" in v),None)
            if install is not None and (auth is None or install<auth):
                problems.append("RUNTIME_INSTALL_BEFORE_EXECUTION_RECHECK_"+name)
            if name=="annual_preflight":
                fetch=next((j for j,v in enumerate(steps)
                            if "Fetch exact accepted EXP-044 source snapshots"==v),
                           None)
                if fetch is not None and (auth is None or fetch<auth):
                    problems.append("SOURCE_SNAPSHOT_METADATA_BEFORE_AUTHORIZATION")
        if len(tuple(CELL_LINE.finditer(source)))!=18:
            problems.append("SOURCE_MATRIX_NOT_EXACTLY_18_CELLS")

    return {
        "classification":"SOURCE_ONLY_WORKFLOW_ORDER_NONAUTHORITATIVE",
        "status":"BLOCKED",
        "can_authorize_dispatch":False,
        "independent_os_proof_verified":False,
        "immutable_annual_admission_verified":False,
        "may_access_protected_evidence":False,
        "may_install_workflow_or_policy":False,
        "may_trade":False,
        "gate_states":{"DEC-650/#820":"BLOCKED",
                       "DEC-651/#821/#779":"BLOCKED"},
        "job_steps":inventory,
        "blockers":tuple(problems),
    }
