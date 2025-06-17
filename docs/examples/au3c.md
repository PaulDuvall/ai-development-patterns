# Failed Authentication Tracking

Examples for [^au3c] in tracking failed attempts and returning generic error messages:

**Example**: User enters wrong password for their account

<user>
User tries to log in with email "alice@company.com" and password "wrongpassword123" but their actual password is "correctpassword456".
</user>

The system should:
- Return exactly the same error message as if the email didn't exist: "Invalid email or password"
- Increment the failed attempt counter for both the email and the IP address
- Take approximately the same amount of time as a successful login (to prevent timing attacks)
- Log the failed attempt with timestamp, IP address, and attempted email (but not the password)

**Example**: User enters email that doesn't exist in system

<user>
User tries to log in with "nonexistent@domain.com" and any password, but no account exists for this email.
</user>

The system should:
- Return the identical error message: "Invalid email or password"
- Still increment the failed attempt counter for the IP address
- Simulate the same processing time as checking a real password hash
- Not reveal that the email address is not registered in the system

**Example**: Multiple failed attempts from same user

<user>
User "bob@company.com" has already failed to log in twice in the last 10 minutes. They now attempt a third login with the wrong password.
</user>

The system should:
- Return the same generic error message: "Invalid email or password"
- Increment the failed attempt counter to 3 for both email and IP
- Prepare to trigger rate limiting if they fail again
- Continue to log each attempt for security monitoring

**Example**: Successful login after failed attempts

<user>
User "carol@company.com" has 2 failed login attempts recorded. They now provide the correct email and password combination.
</user>

The system should:
- Successfully authenticate and log them in
- Reset the failed attempt counter for both their email and IP address to zero
- Log the successful authentication event
- Proceed with normal login flow (session creation, redirects, etc.)

**Example**: User enumeration attack attempt

<user>
An attacker systematically tries common email addresses like "admin@company.com", "test@company.com", "user@company.com" with random passwords to see if the accounts exist.
</user>

The system should:
- Return identical "Invalid email or password" messages for all attempts
- Take consistent response times regardless of whether emails exist
- Track all attempts under the attacker's IP address for rate limiting
- Not provide any behavioral hints about which emails are valid accounts

**Example**: Password reset during failed attempt tracking

<user>
User has 2 failed login attempts and instead of trying again, they click "Forgot Password" to reset their password.
</user>

The system should:
- Allow the password reset process to proceed normally
- Keep the existing failed attempt counters (don't reset them)
- Track password reset attempts separately but under the same rate limiting rules
- Reset failed attempt counters only after successful login with the new password