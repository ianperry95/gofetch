import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch }) => {
	try {
		const res = await fetch('/api/collections');
		if (!res.ok) return { collections: [] };
		return { collections: await res.json() };
	} catch {
		return { collections: [] };
	}
};
