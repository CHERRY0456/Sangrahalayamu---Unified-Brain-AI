/**
 * Obfuscates standard authentication string tokens via Base64 encoding for basic visual redaction in cookies.
 */
export function redactAuthToken(token: string): string {
  try {
    if (typeof window !== 'undefined') {
      return window.btoa(token);
    }
    return Buffer.from(token).toString('base64');
  } catch (e) {
    return token;
  }
}

/**
 * Decodes obfuscated Base64 authentication string tokens.
 */
export function decodeRedactedToken(redacted: string): string {
  try {
    if (typeof window !== 'undefined') {
      return window.atob(redacted);
    }
    return Buffer.from(redacted, 'base64').toString('ascii');
  } catch (e) {
    return redacted;
  }
}
