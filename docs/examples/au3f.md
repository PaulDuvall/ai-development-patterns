# Authentication Timeout Requirements

Examples for [^au3f] in authentication timeout handling:

**Example**: User accessing application after extended inactivity

<user>
User logs into the application at 9:00 AM, then leaves for a meeting. At 9:35 AM, they return and try to access their dashboard without logging in again.
</user>

The system should:
- Detect that 35 minutes have passed since last activity
- Invalidate the user's session automatically
- Redirect the user to the login page
- Display message: "Your session has expired for security reasons. Please log in again."

**Example**: User working actively with brief breaks

<user>
User logs in at 9:00 AM and actively uses the application. At 9:25 AM, they step away for 10 minutes. At 9:35 AM, they return and click on a new page in the application.
</user>

The system should:
- Recognize that only 10 minutes passed since last activity (not 35 total)
- Keep the session valid since it's under the 30-minute threshold
- Allow normal access to the requested page
- Reset the inactivity timer to start counting from 9:35 AM

**Example**: User makes API call just before timeout

<user>
User's last activity was at 9:00 AM. At 9:29:50 AM (29 minutes and 50 seconds later), their browser automatically makes an API call to check for notifications.
</user>

The system should:
- Treat the API call as user activity
- Reset the 30-minute timeout timer to start from 9:29:50 AM
- Keep the session valid
- Not expire the session until 9:59:50 AM if no further activity occurs

**Example**: Session timeout during form submission

<user>
User starts filling out a long form at 9:00 AM. They spend 35 minutes carefully completing it, then click "Submit" at 9:35 AM.
</user>

The system should:
- Recognize that the session expired during form completion
- Reject the form submission with a 401 Unauthorized response
- Preserve the form data temporarily if possible
- Redirect to login with message: "Your session expired. Please log in again to submit your form."
- After re-authentication, attempt to restore the form data

**Example**: Multiple tabs with different activity times

<user>
User has the application open in two browser tabs. Tab A last had activity at 9:00 AM, Tab B had activity at 9:20 AM. At 9:35 AM, the user tries to use Tab A.
</user>

The system should:
- Use the most recent activity time (9:20 AM) for session timeout calculation
- Since only 15 minutes have passed since the last activity in Tab B, keep the session valid
- Allow normal access in Tab A
- Update the activity timer to 9:35 AM for both tabs