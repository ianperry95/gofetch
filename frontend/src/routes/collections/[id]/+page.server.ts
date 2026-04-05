import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, params }) => {
	try {
		const res = await fetch(`/api/collections/${params.id}`);
		if (!res.ok) return { collection: null, entries: [] };
		const collection = await res.json();

		// Fetch entries from Miniflux for each entry_id
		const entries = [];
		for (const entryId of collection.entry_ids ?? []) {
			try {
				const entryRes = await fetch(`/api/feed/entry/${entryId}`);
				if (entryRes.ok) entries.push(await entryRes.json());
			} catch {
				// skip failed entries
			}
		}

		return { collection, entries };
	} catch {
		return { collection: null, entries: [] };
	}
};
