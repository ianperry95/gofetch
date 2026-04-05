<script lang="ts">
	import { api } from '$lib/api/client';
	import TagPicker from './TagPicker.svelte';
	import CollectionPicker from './CollectionPicker.svelte';

	interface Props {
		selectedIds: number[];
		onClear: () => void;
		onDone?: () => void;
	}

	let { selectedIds, onClear, onDone }: Props = $props();

	let showTagPicker = $state(false);
	let showCollectionPicker = $state(false);

	async function markRead() {
		await api.feed.updateStatus(selectedIds, 'read');
		onClear();
		onDone?.();
	}

	async function markUnread() {
		await api.feed.updateStatus(selectedIds, 'unread');
		onClear();
		onDone?.();
	}
</script>

{#if selectedIds.length > 0}
	<div class="fixed bottom-4 left-1/2 z-50 flex -translate-x-1/2 items-center gap-2 rounded-xl border border-neutral-200 bg-white px-4 py-2.5 shadow-xl dark:border-neutral-700 dark:bg-neutral-900">
		<span class="text-sm font-medium text-neutral-700 dark:text-neutral-300">
			{selectedIds.length} selected
		</span>

		<div class="mx-1 h-5 w-px bg-neutral-200 dark:bg-neutral-700"></div>

		<button
			onclick={markRead}
			class="rounded-md px-2.5 py-1 text-sm transition-colors hover:bg-neutral-100 dark:hover:bg-neutral-800"
		>
			Mark read
		</button>

		<button
			onclick={markUnread}
			class="rounded-md px-2.5 py-1 text-sm transition-colors hover:bg-neutral-100 dark:hover:bg-neutral-800"
		>
			Mark unread
		</button>

		<div class="relative">
			<button
				onclick={() => { showTagPicker = !showTagPicker; showCollectionPicker = false; }}
				class="rounded-md px-2.5 py-1 text-sm transition-colors hover:bg-neutral-100 dark:hover:bg-neutral-800"
			>
				Tag
			</button>
			{#if showTagPicker}
				<div class="absolute bottom-full left-0 mb-2">
					<TagPicker entryIds={selectedIds} onClose={() => (showTagPicker = false)} />
				</div>
			{/if}
		</div>

		<div class="relative">
			<button
				onclick={() => { showCollectionPicker = !showCollectionPicker; showTagPicker = false; }}
				class="rounded-md px-2.5 py-1 text-sm transition-colors hover:bg-neutral-100 dark:hover:bg-neutral-800"
			>
				Collect
			</button>
			{#if showCollectionPicker}
				<div class="absolute bottom-full left-0 mb-2">
					<CollectionPicker entryIds={selectedIds} onClose={() => (showCollectionPicker = false)} />
				</div>
			{/if}
		</div>

		<div class="mx-1 h-5 w-px bg-neutral-200 dark:bg-neutral-700"></div>

		<button
			onclick={onClear}
			class="rounded-md px-2.5 py-1 text-sm text-neutral-500 transition-colors hover:bg-neutral-100 dark:hover:bg-neutral-800"
		>
			Cancel
		</button>
	</div>
{/if}
