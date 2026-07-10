# Scratchpad - Clock Skew Investigation (2024-01-16)

## Current Exploration

Investigating why JWT verification is failing intermittently (~5% of requests) on api-gateway.

### Hypothesis
Clock skew between auth-service and api-gateway causing `exp` (expiration) claim to fail validation.

### Evidence
- Failures occur ONLY on api-gateway-2 instance (not on -1 or -3)
- `docker exec api-gateway-2 date`: 2024-01-16 14:23:17
- `date` (host): 2024-01-16 14:24:04
- **Clock skew: 47 seconds behind!**
- NTP sync is disabled in docker-compose.yml (found: `sysctls: - net.ipv4.tcp_timestamps=0`)
- Added 60s `clockTolerance` to JWT verification → failures dropped from 5% to 0.1%

### Next Steps
- ✅ Enable NTP sync on api-gateway-2
- ✅ Verify failures drop to 0%
- [ ] Document clock skew tolerance decision in DECISIONS.log
- [ ] Add clock drift monitoring alert

---

## Quick Notes

- JWT library: `jsonwebtoken` v9.0.2
- Test command: `wrk -t4 -c100 -d30s --latency http://api-gateway/health`
- RS256 public key location: `/etc/ssl/jwt-public.pem`
- Useful debug: `docker exec <container> date && date` to compare clocks
- Clock tolerance option: `jwt.verify(token, publicKey, { clockTolerance: 60 })`

Question: Are other services also affected by clock skew?
Answer: Checked user-service and order-service - both have NTP enabled, no issues.

---

## Debug Log

```
14:23 Tried: Increased JWT expiry from 15min to 30min to see if exp-related
Result: Failure rate unchanged (still ~5%)
Next: Not an expiry issue. Check timestamps and clock sync.

14:35 Tried: Added 60s clockTolerance to JWT verification in api-gateway
Result: Failure rate dropped from 5% to 0.1% immediately!
Conclusion: Clock skew is the root cause. But why still 0.1% failures?

14:42 Tried: Checked clock on api-gateway-2 vs host
Result: api-gateway-2 is 47 seconds behind host time
Conclusion: NTP sync is disabled. Need to enable.

14:48 Tried: Enabled NTP sync in docker-compose.yml for api-gateway-2
Result: Clock synchronized after restart, failures dropped to 0%
Conclusion: Problem solved! Document tolerance decision.

15:05 Tried: Removed clockTolerance to verify it's working
Result: Failures returned (1-2%)
Conclusion: Keep 60s tolerance as safety margin for NTP delays/failures
```

---

## Ideas for Future

- Add health check that compares container clock to NTP server
- Alert if clock drift exceeds 10 seconds
- Consider using `nbf` (not before) claim for additional validation
- Look into distributed tracing correlation IDs for debugging

---

[CLEAR ABOVE AFTER MOVING INSIGHTS TO NOTES.MD AND DECISIONS.LOG]
