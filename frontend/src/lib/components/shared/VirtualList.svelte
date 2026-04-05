<script lang="ts">
	import { onMount } from 'svelte';

	interface Props {
		items: unknown[];
		itemHeight: number;
		overscan?: number;
		children: (item: unknown, index: number) => any;
	}

	let { items, itemHeight, overscan = 5, children }: Props = $props();

	let container: HTMLDivElement;
	let scrollTop = $state(0);
	let containerHeight = $state(600);

	let totalHeight = $derived(items.length * itemHeight);
	let startIndex = $derived(Math.max(0, Math.floor(scrollTop / itemHeight) - overscan));
	let endIndex = $derived(
		Math.min(items.length, Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan)
	);
	let visibleItems = $derived(items.slice(startIndex, endIndex));
	let offsetY = $derived(startIndex * itemHeight);

	function onScroll() {
		scrollTop = container.scrollTop;
	}

	onMount(() => {
		containerHeight = container.clientHeight;
		const observer = new ResizeObserver((entries) => {
			containerHeight = entries[0].contentRect.height;
		});
		observer.observe(container);
		return () => observer.disconnect();
	});

	export function scrollToIndex(index: number) {
		if (container) {
			const top = index * itemHeight;
			container.scrollTo({ top, behavior: 'smooth' });
		}
	}
</script>

<div
	bind:this={container}
	onscroll={onScroll}
	class="flex-1 overflow-y-auto"
	style="position: relative;"
>
	<div style="height: {totalHeight}px; position: relative;">
		<div style="transform: translateY({offsetY}px);">
			{#each visibleItems as item, i (startIndex + i)}
				{@render children(item, startIndex + i)}
			{/each}
		</div>
	</div>
</div>
