<script lang="ts">
	import Topbar from '$lib/components/layout/Topbar.svelte';
	import { api } from '$lib/api/client';
	import { invalidateAll } from '$app/navigation';

	let { data } = $props();

	let newName = $state('');
	let newColor = $state('#3b82f6');

	async function createTag() {
		if (!newName.trim()) return;
		await api.tags.create(newName.trim(), newColor);
		newName = '';
		invalidateAll();
	}

	async function deleteTag(id: number) {
		await api.tags.delete(id);
		invalidateAll();
	}
</script>

<Topbar />

<div class="flex-1 overflow-y-auto p-4">
	<h1 class="mb-4 text-xl font-bold text-neutral-900 dark:text-neutral-100">Tags</h1>

	<div class="mb-6 flex items-center gap-2">
		<input
			bind:value={newName}
			placeholder="New tag name..."
			class="rounded-lg border border-neutral-200 bg-transparent px-3 py-2 text-sm dark:border-neutral-700"
			onkeydown={(e) => e.key === 'Enter' && createTag()}
		/>
		<input
			bind:value={newColor}
			type="color"
			class="h-9 w-9 cursor-pointer rounded border border-neutral-200 dark:border-neutral-700"
		/>
		<button
			onclick={createTag}
			disabled={!newName.trim()}
			class="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
		>
			Create
		</button>
	</div>

	{#if data.tags.length === 0}
		<p class="text-sm text-neutral-500">No tags yet. Create one above.</p>
	{:else}
		<div class="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3">
			{#each data.tags as tag (tag.id)}
				<div class="flex items-center justify-between rounded-lg border border-neutral-200 bg-white px-4 py-3 dark:border-neutral-800 dark:bg-neutral-950">
					<div class="flex items-center gap-3">
						{#if tag.color}
							<span class="h-4 w-4 rounded-full" style="background-color: {tag.color}"></span>
						{/if}
						<a
							href="/tags/{encodeURIComponent(tag.name)}"
							class="font-medium text-neutral-900 hover:text-blue-600 dark:text-neutral-100"
						>
							{tag.name}
						</a>
						<span class="text-xs text-neutral-400">{tag.article_count ?? 0}</span>
					</div>
					<button
						onclick={() => deleteTag(tag.id)}
						class="text-sm text-neutral-400 hover:text-red-500"
					>
						Delete
					</button>
				</div>
			{/each}
		</div>
	{/if}
</div>
