import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch }) => {
	try {
		const res = await fetch('/api/tags');
		if (!res.ok) return { tags: [] };
		return { tags: await res.json() };
	} catch {
		return { tags: [] };
	}
};
