"""DEC-1330: pure, SOURCE-ONLY negative proof classification.

Only caller-supplied *plain* Python dictionaries are inspected; custom mapping
hooks and dict subclasses are not consulted as claimed evidence.  No filesystem,
network, GitHub, annual workflow, credentials, or protected evidence is read.
Nothing in this module ever returns positive authorization.  A future real
independent proof gate must be separately designed/reviewed/installed.
"""
from __future__ import annotations

STATIC_BLOCKERS = (
    "INDEPENDENT_PROTECTED_ORIGINAL_OS_NO_WRITE_UNVERIFIED",
    "EXCLUSIVE_IMMUTABLE_ANNUAL_REF_SHA_UNVERIFIED",
    "PRECHECKOUT_PREINSTALL_PREEVIDENCE_GATES_UNINSTALLED",
    "FRESH_RUN385_ATTEMPT1_AND_DISTINCT_DECISION_UNVERIFIED",
    "QUALIFIED_INDEPENDENT_SECURITY_REVIEW_OUTSTANDING",
)
SELF_ASSERTIONS = (
    "status", "can_authorize_dispatch", "independent_os_proof_verified",
    "run385_authorized", "exclusive_admission_verified",
    "passed_ci", "qualified_review_complete",
)
UNTRUSTED_PROOF_FORMS = (
    "public_memfd_seals", "inotify_quiet", "self_signed_sha",
    "public_tmp_fixture", "self_reported_admin_lock",
    "unverified_workflow_ref", "source_only_model",
)


def assess_synthetic_claims(packet: object) -> dict[str, object]:
    """Report negative diagnostic findings; NEVER approve a protected action."""
    findings: list[str] = list(STATIC_BLOCKERS)
    if type(packet) is not dict:
        findings.append("INPUT_NOT_A_MAPPING")
    else:
        if any(packet.get(key) is True for key in SELF_ASSERTIONS):
            findings.append("CALLER_SELF_ASSERTED_AUTHORITY_IGNORED")

        proof = packet.get("proof")
        if proof is None:
            findings.append("INDEPENDENT_PROOF_NOT_SUPPLIED")
        elif type(proof) is not dict:
            findings.append("PROOF_NOT_A_MAPPING")
        else:
            kind = proof.get("kind")
            if type(kind) is str and kind in UNTRUSTED_PROOF_FORMS:
                findings.append("DISPOSABLE_OR_SELF_REPORTED_PROOF_IS_NOT_PROTECTED_WITNESS")
            else:
                findings.append("UNVERIFIABLE_CLAIM_CANNOT_ESTABLISH_TRUST")
            if proof.get("independent") is True:
                findings.append("INDEPENDENCE_SELF_ASSERTION_NOT_AUTHENTICATED")

        annual = packet.get("annual")
        if type(annual) is not dict:
            findings.append("ANNUAL_ADMISSION_DETAILS_MISSING")
        else:
            run_number=annual.get("run_number")
            attempt=annual.get("attempt")
            if (type(run_number) is not int or run_number != 385
                or type(attempt) is not int or attempt != 1):
                findings.append("NOT_THE_EXCLUSIVE_RUN385_ATTEMPT1")
            outcome=annual.get("outcome")
            if type(outcome) is str and outcome in (
                "ambiguous", "failed", "cancelled", "retry", "replacement"
            ):
                findings.append("TERMINAL_NO_RETRY_AMBIGUOUS_OR_FAILED_SLOT")
            expected_sha=annual.get("expected_sha")
            observed_sha=annual.get("observed_sha")
            if (type(expected_sha) is not str or not expected_sha
                or type(observed_sha) is not str or not observed_sha):
                findings.append("SHA_BINDING_IDENTITIES_ABSENT_OR_INVALID")
            elif expected_sha == observed_sha:
                findings.append("SHA_EQUALITY_ALONE_NOT_INDEPENDENT_REF_AUTHORITY")
            else:
                findings.append("SHA_MISMATCH_BLOCKS_ADMISSION")

    # Deliberately no positive branch.  The source-only packet is unauthenticated
    # even when it contains syntactically plausible independently signed claims.
    return {
        "classification": "SOURCE_ONLY_SYNTHETIC_NONAUTHORITATIVE",
        "status": "BLOCKED",
        "can_authorize_dispatch": False,
        "independent_os_proof_verified": False,
        "exclusive_annual_admission_verified": False,
        "run385_action_authorized": False,
        "may_access_protected_evidence": False,
        "may_merge_or_promote": False,
        "may_trade": False,
        "reviewer_evidence_authenticated": False,
        "gate_states": {"DEC-650/#820": "BLOCKED",
                        "DEC-651/#821/#779": "BLOCKED"},
        "blockers": tuple(findings),
    }
