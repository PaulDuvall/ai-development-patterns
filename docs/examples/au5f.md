# Rate Limiting Requirements

Examples for [^au5f] in authentication rate limiting:

**Example**: User with repeated incorrect passwords

<user>
User attempts to log in to their account. They try their password three times in a row, but each time they get it wrong because they're not sure if they changed it recently.
</user>

The system should:
- Allow the first three failed attempts with normal "Invalid email or password" messages
- On the fourth attempt, return a 429 Too Many Requests error
- Display message: "Too many failed login attempts. Please wait 5 minutes before trying again."
- Block all login attempts from that IP address for 5 minutes

**Example**: Multiple users from same office network

<user>
Three different employees in an office are all trying to log in from the same IP address (192.168.1.100). Each person tries their password once and gets it wrong because the system was recently updated.
</user>

The system should:
- Count all three failed attempts as coming from the same IP address
- After the third failure (even though from different users), trigger rate limiting
- Block the fourth login attempt from anyone at that IP address
- Display message: "Too many failed login attempts from this location. Please wait 5 minutes."

**Example**: User eventually remembers correct password

<user>
User has been rate-limited after 3 failed attempts. They wait 6 minutes, then remember their correct password and try to log in again.
</user>

The system should:
- Allow the login attempt since the 5-minute penalty has expired
- Authenticate successfully with the correct password
- Reset the failed attempt counter to zero
- Allow normal login behavior going forward

**Example**: Attacker with persistent attempts

<user>
An attacker from IP address 203.0.113.5 triggers rate limiting by failing 3 login attempts. After waiting 5 minutes, they immediately fail 3 more attempts.
</user>

The system should:
- Apply rate limiting again after the second set of 3 failures
- Increase the penalty duration (e.g., to 10 minutes for the second offense)
- Continue escalating penalties for repeated violations from the same IP
- Log all attempts for security monitoring

**Example**: User needs immediate access during rate limit

<user>
A user has been rate-limited but needs immediate access to their account for a business emergency. They contact IT support.
</user>

The system should:
- Provide an administrative override mechanism for support staff
- Require proper authorization and logging for any rate limit resets
- Allow IT support to temporarily whitelist the IP or clear the rate limit
- Maintain audit trail of all administrative overrides

**Example**: Password reset during rate limit

<user>
User is rate-limited on login attempts but realizes they need to reset their password. They try to use the "Forgot Password" feature.
</user>

The system should:
- Apply rate limiting to password reset attempts as well as login attempts
- Count password reset failures toward the same rate limit threshold
- Prevent attackers from switching between login and password reset to bypass limits
- Display consistent rate limiting messages across all authentication endpoints