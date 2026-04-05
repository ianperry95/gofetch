<script lang="ts">
	import { keyboard } from '$lib/stores/keyboard.svelte';

	const shortcuts = [
		{ key: 'j', desc: 'Next article' },
		{ key: 'k', desc: 'Previous article' },
		{ key: 'o / Enter', desc: 'Open article' },
		{ key: 's', desc: 'Toggle star' },
		{ key: '?', desc: 'Toggle this help' },
		{ key: 'Esc', desc: 'Close / go back' }
	];
</script>

{#if keyboard.showHelp}
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div
		class="fixed inset-0 z-[100] flex items-center justify-center bg-black/50"
		onclick={() => (keyboard.showHelp = false)}
		onkeydown={(e) => e.key === 'Escape' && (keyboard.showHelp = false)}
	>
		<!-- svelte-ignore a11y_no_static_element_interactions -->
		<div
			class="w-80 rounded-xl border border-neutral-200 bg-white p-6 shadow-2xl dark:border-neutral-700 dark:bg-neutral-900"
			onclick={(e) => e.stopPropagation()}
		>
			<div class="mb-4 flex items-center justify-between">
				<h2 class="text-lg font-semibold text-neutral-900 dark:text-neutral-100">Keyboard shortcuts</h2>
				<button
					onclick={() => (keyboard.showHelp = false)}
					class="text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-300"
				>&times;</button>
			</div>

			<div class="space-y-2">
				{#each shortcuts as { key, desc }}
					<div class="flex items-center justify-between">
						<span class="text-sm text-neutral-600 dark:text-neutral-400">{desc}</span>
						<kbd class="rounded bg-neutral-100 px-2 py-0.5 text-xs font-mono font-medium text-neutral-700 dark:bg-neutral-800 dark:text-neutral-300">
							{key}
						</kbd>
					</div>
				{/each}
			</div>
		</div>
	</div>
{/if}
