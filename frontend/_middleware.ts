import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const sessionCookie = request.cookies.get('ib-session-token')?.value;
  const { pathname } = request.nextUrl;

  // 1. Redirect root `/` to `/login` always
  if (pathname === '/') {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // Identify protected routing categories
  const isProtectedRoute = 
    pathname.startsWith('/dashboard') ||
    pathname.startsWith('/upload') ||
    pathname.startsWith('/processing') ||
    pathname.startsWith('/chat') ||
    pathname.startsWith('/transparency') ||
    pathname.startsWith('/audit') ||
    pathname.startsWith('/history') ||
    pathname.startsWith('/settings');

  // 2. Enforce login shields on protected workspace pathways
  if (isProtectedRoute && !sessionCookie) {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('callbackUrl', pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

// Optimize middleware execution scope matching only application route channels
export const config = {
  matcher: [
    '/',
    '/dashboard/:path*',
    '/upload/:path*',
    '/processing/:path*',
    '/chat/:path*',
    '/transparency/:path*',
    '/audit/:path*',
    '/history/:path*',
    '/settings/:path*',
    '/login',
  ],
};
