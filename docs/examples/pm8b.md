# Payment Transaction Blocking Specification {#pm8b}

## Overview {#overview}
This specification defines requirements for blocking suspicious payment transactions, including criteria for blocking decisions, response procedures, and user communication protocols.

## Blocking Criteria {#blocking_criteria authority=platform}

### Risk-Based Blocking {#risk_blocking authority=system}
The system MUST:
- Block transactions exceeding critical risk score thresholds (>90/100) [^pm8b1]
- Implement immediate blocking for transactions from blacklisted sources [^pm8b2]
- Block transactions exceeding velocity limits per user or card [^pm8b3]
- Prevent transactions that fail multiple verification attempts [^pm8b4]

### Compliance-Based Blocking {#compliance_blocking authority=platform}
The system MUST:
- Block transactions to sanctioned entities or restricted countries [^pm8b5]
- Prevent transactions exceeding regulatory reporting thresholds [^pm8b6]
- Block transactions during system maintenance or security incidents [^pm8b7]
- Implement account-level blocks for confirmed fraud cases [^pm8b8]

### Automated Response {#automated_response authority=system}
The system MUST:
- Execute blocking decisions within 500ms of risk assessment [^pm8b9]
- Generate appropriate error codes for different blocking reasons [^pm8b10]
- Trigger immediate fraud investigation workflows [^pm8b11]
- Notify relevant security teams of high-risk blocking events [^pm8b12]

## User Communication {#user_communication authority=system}

### Error Messages {#error_messages authority=system}
The system MUST:
- Provide generic error messages that don't reveal fraud detection methods [^pm8b13]
- Include customer service contact information for blocked transactions [^pm8b14]
- Suggest alternative payment methods when appropriate [^pm8b15]
- Log all user-facing error messages for analysis [^pm8b16]

### Notification Procedures {#notifications authority=system}
The system MUST:
- Send transaction blocking notifications via secure channels [^pm8b17]
- Include transaction reference numbers for customer service [^pm8b18]
- Provide clear steps for dispute resolution and account recovery [^pm8b19]
- Maintain notification delivery confirmation logs [^pm8b20]

## Manual Review Process {#manual_review authority=system}

### Review Queue Management {#review_queue authority=system}
The system MUST:
- Queue blocked transactions for human review within defined SLAs [^pm8b21]
- Prioritize review based on transaction value and user history [^pm8b22]
- Provide reviewers with complete transaction context and risk factors [^pm8b23]
- Track review decision times and accuracy metrics [^pm8b24]

## Evaluation Cases {#evaluation}

[^pm8b1]: tests/blocking/test_risk_threshold_blocking.py
[^pm8b2]: tests/blocking/test_blacklist_blocking.py
[^pm8b3]: tests/blocking/test_velocity_limit_blocking.py
[^pm8b4]: tests/blocking/test_verification_failure_blocking.py
[^pm8b5]: tests/blocking/test_sanctions_blocking.py
[^pm8b6]: tests/blocking/test_regulatory_threshold_blocking.py
[^pm8b7]: tests/blocking/test_maintenance_blocking.py
[^pm8b8]: tests/blocking/test_account_level_blocking.py
[^pm8b9]: tests/blocking/test_response_time.py
[^pm8b10]: tests/blocking/test_error_code_generation.py
[^pm8b11]: tests/blocking/test_investigation_triggers.py
[^pm8b12]: tests/blocking/test_security_notifications.py
[^pm8b13]: tests/blocking/test_generic_error_messages.py
[^pm8b14]: tests/blocking/test_customer_service_info.py
[^pm8b15]: tests/blocking/test_alternative_suggestions.py
[^pm8b16]: tests/blocking/test_error_message_logging.py
[^pm8b17]: tests/blocking/test_secure_notifications.py
[^pm8b18]: tests/blocking/test_reference_numbers.py
[^pm8b19]: tests/blocking/test_dispute_resolution.py
[^pm8b20]: tests/blocking/test_delivery_confirmation.py
[^pm8b21]: tests/blocking/test_review_queue_sla.py
[^pm8b22]: tests/blocking/test_review_prioritization.py
[^pm8b23]: tests/blocking/test_review_context.py
[^pm8b24]: tests/blocking/test_review_metrics.py