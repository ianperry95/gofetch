import type { Handle } from '@sveltejs/kit';

const API_UPSTREAM = process.env.GOFETCH_API_URL || 'http://localhost:8000';

export const handle: Handle = async ({ event, resolve }) => {
	// Proxy /api/* requests to the FastAPI backend
	if (event.url.pathname.startsWith('/api/')) {
		const upstream = `${API_UPSTREAM}${event.url.pathname}${event.url.search}`;

		const isSSE = event.url.pathname === '/api/events';

		const res = await fetch(upstream, {
			method: event.request.method,
			headers: event.request.headers,
			body: event.request.method !== 'GET' ? await event.request.text() : undefined
		});

		const headers = new Headers(res.headers);
		if (isSSE) {
			headers.set('Content-Type', 'text/event-stream');
			headers.set('Cache-Control', 'no-cache');
			headers.set('Connection', 'keep-alive');
		}

		return new Response(res.body, {
			status: res.status,
			statusText: res.statusText,
			headers
		});
	}

	return resolve(event);
};
