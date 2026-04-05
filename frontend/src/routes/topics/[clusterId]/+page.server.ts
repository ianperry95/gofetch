import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, params }) => {
	try {
		const res = await fetch(`/api/topics/${params.clusterId}`);
		if (!res.ok) return { cluster: null };
		return { cluster: await res.json() };
	} catch {
		return { cluster: null };
	}
};
