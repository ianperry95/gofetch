import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, url }) => {
	const sort = url.searchParams.get('sort') || 'ranked';
	const feedId = url.searchParams.get('feed_id');
	const limit = 50;

	const params = new URLSearchParams({
		sort,
		limit: String(limit),
		offset: '0',
		status: 'unread',
		hide_duplicates: 'true'
	});

	if (feedId) params.set('feed_id', feedId);

	try {
		const res = await fetch(`/api/feed?${params}`);
		if (!res.ok) return { entries: [], total: 0 };
		return await res.json();
	} catch {
		return { entries: [], total: 0 };
	}
};
