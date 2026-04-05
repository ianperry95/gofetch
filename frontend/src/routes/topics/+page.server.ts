import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch }) => {
	try {
		const res = await fetch('/api/topics?limit=20');
		if (!res.ok) return { clusters: [] };
		return { clusters: await res.json() };
	} catch {
		return { clusters: [] };
	}
};
