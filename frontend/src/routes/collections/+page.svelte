<script lang="ts">
	import Topbar from '$lib/components/layout/Topbar.svelte';
	import { api } from '$lib/api/client';
	import { invalidateAll } from '$app/navigation';

	let { data } = $props();

	let newName = $state('');

	async function createCollection() {
		if (!newName.trim()) return;
		await api.collections.create({ name: newName.trim() });
		newName = '';
		invalidateAll();
	}

	async function deleteCollection(id: number) {
		await api.collections.delete(id);
		invalidateAll();
	}
</script>

<Topbar />

<div class="flex-1 overflow-y-auto p-4">
	<h1 class="mb-4 text-xl font-bold text-neutral-900 dark:text-neutral-100">Collections</h1>

	<div class="mb-6 flex items-center gap-2">
		<input
			bind:value={newName}
			placeholder="New collection name..."
			class="rounded-lg border border-neutral-200 bg-transparent px-3 py-2 text-sm dark:border-neutral-700"
			onkeydown={(e) => e.key === 'Enter' && createCollection()}
		/>
		<button
			onclick={createCollection}
			disabled={!newName.trim()}
			class="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
		>
			Create
		</button>
	</div>

	{#if data.collections.length === 0}
		<p class="text-sm text-neutral-500">No collections yet. Create one above.</p>
	{:else}
		<div class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
			{#each data.collections as collection (collection.id)}
				<div class="flex items-center justify-between rounded-xl border border-neutral-200 bg-white p-4 dark:border-neutral-800 dark:bg-neutral-950">
					<a
						href="/collections/{collection.id}"
						class="flex items-center gap-3 hover:text-blue-600"
					>
						<span class="text-xl">{collection.icon || '📁'}</span>
						<div>
							<div class="font-medium text-neutral-900 dark:text-neutral-100">
								{collection.name}
							</div>
							<div class="text-xs text-neutral-500">
								{collection.article_count ?? 0} articles
								{#if collection.is_smart}
									<span class="ml-1 rounded bg-purple-100 px-1.5 py-0.5 text-purple-700 dark:bg-purple-900 dark:text-purple-300">
										Smart
									</span>
								{/if}
							</div>
						</div>
					</a>
					<button
						onclick={() => deleteCollection(collection.id)}
						class="text-sm text-neutral-400 hover:text-red-500"
					>
						Delete
					</button>
				</div>
			{/each}
		</div>
	{/if}
</div>
