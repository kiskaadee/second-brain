# Authentication & Authorization Notes

## JWT (JSON Web Tokens)
- A compact, URL-safe means of representing claims to be transferred between two parties.
- Consists of three parts separated by dots: `Header.Payload.Signature`
- **Header:** Algorithm & token type (e.g. HS256, JWT).
- **Payload:** Claims (e.g. user ID, expiration, roles).
- **Signature:** Verifies that the sender of the JWT is who it says it is and ensures the message wasn't changed along the way.

## Session/JWT flow
1. Client logs in with credentials.
2. Server verifies and issues an Access Token (short-lived, e.g. 15m) and a Refresh Token (long-lived, e.g. 7 days).
3. Client stores Refresh Token in a secure, `HttpOnly` cookie and Access Token in memory or storage.
4. Client includes Access Token in the Authorization header (`Bearer <token>`) for protected requests.
5. When Access Token expires, client calls `/refresh` with the Refresh Token to get a new Access Token.
