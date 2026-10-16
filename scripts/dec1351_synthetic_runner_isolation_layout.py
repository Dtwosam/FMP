"""DEC-1351: offline annual runner isolation layout rehearsal.

Inputs are caller-provided symbolic PUBLIC fixture values only. This module
does not create a process, mount, network connection, GitHub action or file
descriptor; it never checks or opens protected annual objects.
Even a complete model returns BLOCKED and no authorization.
"""
from __future__ import annotations

STAGES=("trusted_staging","restricted_consumer","trusted_uploader")
FIELDS=("stages","original_source_mode","scratch_mode","publication",
        "consumer","scope")
CONSUMER_FIELDS=(
    "uid_isolated","no_new_privs","can_sudo","ambient_caps",
    "inherited_writable_source_fds","inherited_writable_source_maps",
    "fd0","fd1","fd2","policy_before_first_access",
)


def _exact_string(value: object, expected: str) -> bool:
    """Refuse custom __eq__ on symbolic user values before comparison."""
    return type(value) is str and value == expected


def assess_synthetic_runner_layout(packet: object) -> dict[str, object]:
    violations=[]
    # Built-in string keys are checked *before* set equality or get
    # so malicious hash-colliding key objects cannot invoke __eq__.
    if type(packet) is not dict or any(type(k) is not str for k in packet):
        violations.append("UNTRUSTED_LAYOUT_INPUT")
    else:
        if set(packet) != set(FIELDS):
            violations.append("MISSING_OR_EXTRA_LAYOUT_FIELDS")
        stages=packet.get("stages")
        if (type(stages) is not tuple
            or len(stages) != len(STAGES)
            or any(not _exact_string(value,expected)
                   for value,expected in zip(stages,STAGES))):
            violations.append("STAGING_CONSUMER_UPLOADER_ORDER_NOT_PINNED")
        if not _exact_string(packet.get("original_source_mode"),"read_only"):
            violations.append("SYNTHETIC_ORIGINAL_NOT_READONLY")
        if not _exact_string(packet.get("scratch_mode"),"separate_read_write"):
            violations.append("SCRATCH_NOT_INDEPENDENT_OF_ORIGINAL")
        if not _exact_string(packet.get("publication"),"trusted_external_only"):
            violations.append("REPORT_PUBLICATION_NOT_EXTERNAL")
        if not _exact_string(packet.get("scope"),"generated_public_only"):
            violations.append("UNAUTHORIZED_REAL_SOURCE_SCOPE")
        consumer=packet.get("consumer")
        # The nested dictionary is independently checked before set()
        # equality and any subsequent known-field lookups.
        if type(consumer) is not dict or any(
            type(k) is not str for k in consumer
        ):
            violations.append("UNTRUSTED_CONSUMER_SPEC")
        else:
            if set(consumer) != set(CONSUMER_FIELDS):
                violations.append("MISSING_OR_EXTRA_CONSUMER_FIELDS")
            if (consumer.get("uid_isolated") is not True
                or consumer.get("no_new_privs") is not True
                or consumer.get("can_sudo") is not False
                or type(consumer.get("ambient_caps")) is not int
                or consumer.get("ambient_caps") != 0):
                violations.append("CONSUMER_PRIVILEGE_ISOLATION_UNVERIFIED")
            if (type(consumer.get("inherited_writable_source_fds")) is not int
                or consumer.get("inherited_writable_source_fds") != 0
                or type(consumer.get("inherited_writable_source_maps")) is not int
                or consumer.get("inherited_writable_source_maps") != 0):
                violations.append("INHERITED_ORIGINAL_WRITE_CAPABILITY_EXISTS")
            if (not _exact_string(consumer.get("fd0"),"safe_input")
                or not _exact_string(consumer.get("fd1"),"scratch_output")
                or not _exact_string(consumer.get("fd2"),"scratch_error")):
                violations.append("STANDARD_DESCRIPTOR_TARGETS_NOT_SAFE")
            if consumer.get("policy_before_first_access") is not True:
                violations.append("ORIGINAL_ACCESS_PRECEDES_POLICY")

    # This is an internally consistent, unverified design model only.
    # No claimed success can authenticate OS enforcement or one-shot admission.
    return {
        "classification":"SOURCE_ONLY_LAYOUT_NONAUTHORITATIVE",
        "design_consistent":len(violations)==0,
        "status":"BLOCKED",
        "independent_os_proof_verified":False,
        "immutable_annual_admission_verified":False,
        "can_authorize_dispatch":False,
        "may_access_protected_evidence":False,
        "may_install_workflow_or_policy":False,
        "may_trade":False,
        "gate_states":{"DEC-650/#820":"BLOCKED",
                       "DEC-651/#821/#779":"BLOCKED"},
        "violations":tuple(violations),
    }
