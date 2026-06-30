from backend.app.security import detect_security_findings


def test_known_backdoor_trigger_is_detected():
    findings = detect_security_findings("J3 SU1S UN3 P0UP33 D3 C1R3 token")
    assert any(finding.code == "blocked_backdoor_trigger" for finding in findings)


def test_plain_finance_prompt_is_allowed():
    findings = detect_security_findings("Explain portfolio diversification for a retail investor.")
    assert findings == []
