<script lang="ts">
	import { api, type CollectionData } from '$lib/api/client';

	interface Props {
		entryIds: number[];
		onClose?: () => void;
	}

	let { entryIds, onClose }: Props = $props();

	let collections: CollectionData[] = $state([]);
	let newName = $state('');
	let loading = $state(false);

	async function loadCollections() {
		collections = await api.collections.list();
	}

	async function addToCollection(collection: CollectionData) {
		loading = true;
		try {
			await api.collections.addArticles(collection.id, entryIds);
		} finally {
			loading = false;
		}
	}

	async function createAndAdd() {
		if (!newName.trim()) return;
		loading = true;
		try {
			const collection = await api.collections.create({ name: newName.trim() });
			await api.collections.addArticles(collection.id, entryIds);
			newName = '';
			await loadCollections();
		} finally {
			loading = false;
		}
	}

	$effect(() => {
		loadCollections();
	});
</script>

<div class="w-64 rounded-lg border border-neutral-200 bg-white p-3 shadow-lg dark:border-neutral-700 dark:bg-neutral-900">
	<div class="mb-2 flex items-center justify-between">
		<span class="text-sm font-medium text-neutral-700 dark:text-neutral-300">Collections</span>
		{#if onClose}
			<button onclick={onClose} class="text-neutral-400 hover:text-neutral-600">&times;</button>
		{/if}
	</div>

	<div class="mb-2 flex gap-1">
		<input
			bind:value={newName}
			placeholder="New collection..."
			class="flex-1 rounded border border-neutral-200 bg-transparent px-2 py-1 text-sm dark:border-neutral-700"
			onkeydown={(e) => e.key === 'Enter' && createAndAdd()}
		/>
		<button
			onclick={createAndAdd}
			disabled={!newName.trim() || loading}
			class="rounded bg-blue-600 px-2 py-1 text-xs font-medium text-white hover:bg-blue-700 disabled:opacity-50"
		>
			+
		</button>
	</div>

	<div class="max-h-48 overflow-y-auto">
		{#each collections as collection (collection.id)}
			<button
				onclick={() => addToCollection(collection)}
				disabled={loading}
				class="flex w-full items-center gap-2 rounded px-2 py-1.5 text-sm transition-colors hover:bg-neutral-100 dark:hover:bg-neutral-800"
			>
				<span class="shrink-0">{collection.icon || '📁'}</span>
				<span class="truncate">{collection.name}</span>
				{#if collection.article_count}
					<span class="ml-auto text-xs text-neutral-400">{collection.article_count}</span>
				{/if}
			</button>
		{/each}
	</div>
</div>
