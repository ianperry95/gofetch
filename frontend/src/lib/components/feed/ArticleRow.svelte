<script lang="ts">
	import type { Entry } from '$lib/api/types';
	import TimeAgo from '$lib/components/shared/TimeAgo.svelte';
	import StarButton from '$lib/components/curation/StarButton.svelte';

	interface Props {
		entry: Entry;
		selectable?: boolean;
		selected?: boolean;
		focused?: boolean;
		index?: number;
		onSelect?: (id: number) => void;
	}

	let { entry, selectable = false, selected = false, focused = false, index, onSelect }: Props = $props();
</script>

<article
	data-entry-index={index}
	class="group flex items-center gap-3 border-b px-4 py-3 transition-colors hover:bg-neutral-50 dark:hover:bg-neutral-900/50"
	class:border-neutral-100={!selected}
	class:dark:border-neutral-900={!selected}
	class:bg-blue-50={selected && !focused}
	class:bg-blue-100={focused}
	class:dark:bg-blue-950={selected || focused}
>
	{#if selectable}
		<input
			type="checkbox"
			checked={selected}
			onchange={() => onSelect?.(entry.id)}
			class="h-3.5 w-3.5 rounded border-neutral-300"
		/>
	{/if}

	<StarButton entryId={entry.id} starred={entry.starred} />

	<a href="/article/{entry.id}" class="flex min-w-0 flex-1 items-center gap-3">
		<div class="min-w-0 flex-1">
			<h2 class="truncate text-sm font-medium text-neutral-900 group-hover:text-blue-600 dark:text-neutral-100 dark:group-hover:text-blue-400">
				{entry.title}
			</h2>
		</div>

		<span class="shrink-0 text-xs text-neutral-500">
			{entry.feed?.title ?? ''}
		</span>

		<span class="shrink-0 text-xs text-neutral-400">
			<TimeAgo date={entry.published_at} />
		</span>

		{#if entry.reading_time}
			<span class="shrink-0 text-xs text-neutral-400">
				{entry.reading_time}m
			</span>
		{/if}
	</a>
</article>
