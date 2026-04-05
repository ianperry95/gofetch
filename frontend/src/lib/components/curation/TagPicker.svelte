<script lang="ts">
	import { api, type TagData } from '$lib/api/client';

	interface Props {
		entryIds: number[];
		onClose?: () => void;
	}

	let { entryIds, onClose }: Props = $props();

	let tags: TagData[] = $state([]);
	let newTagName = $state('');
	let loading = $state(false);

	async function loadTags() {
		tags = await api.tags.list();
	}

	async function toggleTag(tag: TagData) {
		loading = true;
		try {
			await api.tags.tagArticles(tag.id, entryIds);
		} finally {
			loading = false;
		}
	}

	async function createAndApply() {
		if (!newTagName.trim()) return;
		loading = true;
		try {
			const tag = await api.tags.create(newTagName.trim());
			await api.tags.tagArticles(tag.id, entryIds);
			newTagName = '';
			await loadTags();
		} finally {
			loading = false;
		}
	}

	$effect(() => {
		loadTags();
	});
</script>

<div class="w-64 rounded-lg border border-neutral-200 bg-white p-3 shadow-lg dark:border-neutral-700 dark:bg-neutral-900">
	<div class="mb-2 flex items-center justify-between">
		<span class="text-sm font-medium text-neutral-700 dark:text-neutral-300">Tags</span>
		{#if onClose}
			<button onclick={onClose} class="text-neutral-400 hover:text-neutral-600">&times;</button>
		{/if}
	</div>

	<div class="mb-2 flex gap-1">
		<input
			bind:value={newTagName}
			placeholder="New tag..."
			class="flex-1 rounded border border-neutral-200 bg-transparent px-2 py-1 text-sm dark:border-neutral-700"
			onkeydown={(e) => e.key === 'Enter' && createAndApply()}
		/>
		<button
			onclick={createAndApply}
			disabled={!newTagName.trim() || loading}
			class="rounded bg-blue-600 px-2 py-1 text-xs font-medium text-white hover:bg-blue-700 disabled:opacity-50"
		>
			+
		</button>
	</div>

	<div class="max-h-48 overflow-y-auto">
		{#each tags as tag (tag.id)}
			<button
				onclick={() => toggleTag(tag)}
				disabled={loading}
				class="flex w-full items-center gap-2 rounded px-2 py-1.5 text-sm transition-colors hover:bg-neutral-100 dark:hover:bg-neutral-800"
			>
				{#if tag.color}
					<span
						class="h-3 w-3 shrink-0 rounded-full"
						style="background-color: {tag.color}"
					></span>
				{/if}
				<span class="truncate">{tag.name}</span>
				{#if tag.article_count}
					<span class="ml-auto text-xs text-neutral-400">{tag.article_count}</span>
				{/if}
			</button>
		{/each}
	</div>
</div>
