import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, params }) => {
	const res = await fetch(`/api/feed/entry/${params.id}`);
	if (!res.ok) {
		return { entry: null };
	}
	return { entry: await res.json() };
};
