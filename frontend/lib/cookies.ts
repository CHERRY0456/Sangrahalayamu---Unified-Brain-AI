/**
 * Writes a cookie client-side.
 */
export function setCookie(name: string, value: string, days?: number) {
  if (typeof document === 'undefined') return;
  if (days !== undefined) {
    const expires = new Date();
    expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000);
    document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/;SameSite=Lax`;
  } else {
    // Session Cookie (in-memory only, deleted on browser close)
    document.cookie = `${name}=${value};path=/;SameSite=Lax`;
  }
}

/**
 * Reads a cookie client-side.
 */
export function getCookie(name: string): string | null {
  if (typeof document === 'undefined') return null;
  const nameEQ = name + '=';
  const ca = document.cookie.split(';');
  for (let i = 0; i < ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) === ' ') c = c.substring(1, c.length);
    if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
  }
  return null;
}

/**
 * Erases a cookie client-side.
 */
export function eraseCookie(name: string) {
  if (typeof document === 'undefined') return;
  document.cookie = `${name}=; Max-Age=-99999999;path=/;SameSite=Lax`;
}
