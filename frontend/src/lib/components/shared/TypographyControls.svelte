<script lang="ts">
	import { preferences } from '$lib/stores/preferences.svelte';

	let open = $state(false);

	const fonts = [
		{ value: 'system', label: 'System' },
		{ value: 'serif', label: 'Serif' },
		{ value: 'mono', label: 'Mono' }
	];

	function adjustFontSize(delta: number) {
		const next = preferences.articleFontSize + delta;
		if (next >= 14 && next <= 28) {
			preferences.articleFontSize = next;
			preferences.save();
		}
	}

	function adjustWidth(delta: number) {
		const next = preferences.articleMaxWidth + delta;
		if (next >= 480 && next <= 1080) {
			preferences.articleMaxWidth = next;
			preferences.save();
		}
	}

	function setFont(font: string) {
		preferences.articleFont = font;
		preferences.save();
	}
</script>

<div class="relative">
	<button
		onclick={() => (open = !open)}
		class="rounded-md p-1.5 transition-colors hover:bg-neutral-100 dark:hover:bg-neutral-800"
		aria-label="Typography settings"
	>
		<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h8m-8 6h16" />
		</svg>
	</button>

	{#if open}
		<!-- svelte-ignore a11y_no_static_element_interactions -->
		<div
			class="absolute right-0 top-full z-50 mt-2 w-64 rounded-lg border border-neutral-200 bg-white p-4 shadow-xl dark:border-neutral-700 dark:bg-neutral-900"
			onkeydown={(e) => e.key === 'Escape' && (open = false)}
		>
			<h3 class="mb-3 text-xs font-semibold tracking-wider text-neutral-500 uppercase">Typography</h3>

			<!-- Font size -->
			<div class="mb-4">
				<div class="mb-1.5 flex items-center justify-between">
					<span class="text-sm text-neutral-600 dark:text-neutral-400">Font size</span>
					<span class="text-sm font-medium text-neutral-900 dark:text-neutral-100">{preferences.articleFontSize}px</span>
				</div>
				<div class="flex items-center gap-2">
					<button
						onclick={() => adjustFontSize(-1)}
						disabled={preferences.articleFontSize <= 14}
						class="flex h-8 w-8 items-center justify-center rounded border border-neutral-200 text-sm transition-colors hover:bg-neutral-100 disabled:opacity-30 dark:border-neutral-700 dark:hover:bg-neutral-800"
					>A</button>
					<div class="flex-1">
						<div class="relative h-1.5 rounded-full bg-neutral-200 dark:bg-neutral-700">
							<div
								class="absolute h-1.5 rounded-full bg-blue-500"
								style="width: {((preferences.articleFontSize - 14) / 14) * 100}%"
							></div>
						</div>
					</div>
					<button
						onclick={() => adjustFontSize(1)}
						disabled={preferences.articleFontSize >= 28}
						class="flex h-8 w-8 items-center justify-center rounded border border-neutral-200 text-lg transition-colors hover:bg-neutral-100 disabled:opacity-30 dark:border-neutral-700 dark:hover:bg-neutral-800"
					>A</button>
				</div>
			</div>

			<!-- Line width -->
			<div class="mb-4">
				<div class="mb-1.5 flex items-center justify-between">
					<span class="text-sm text-neutral-600 dark:text-neutral-400">Line width</span>
					<span class="text-sm font-medium text-neutral-900 dark:text-neutral-100">{preferences.articleMaxWidth}px</span>
				</div>
				<div class="flex items-center gap-2">
					<button
						onclick={() => adjustWidth(-40)}
						disabled={preferences.articleMaxWidth <= 480}
						class="flex h-8 w-8 items-center justify-center rounded border border-neutral-200 transition-colors hover:bg-neutral-100 disabled:opacity-30 dark:border-neutral-700 dark:hover:bg-neutral-800"
					>
						<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12h10" />
						</svg>
					</button>
					<div class="flex-1">
						<div class="relative h-1.5 rounded-full bg-neutral-200 dark:bg-neutral-700">
							<div
								class="absolute h-1.5 rounded-full bg-blue-500"
								style="width: {((preferences.articleMaxWidth - 480) / 600) * 100}%"
							></div>
						</div>
					</div>
					<button
						onclick={() => adjustWidth(40)}
						disabled={preferences.articleMaxWidth >= 1080}
						class="flex h-8 w-8 items-center justify-center rounded border border-neutral-200 transition-colors hover:bg-neutral-100 disabled:opacity-30 dark:border-neutral-700 dark:hover:bg-neutral-800"
					>
						<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v12m-5-6h10" />
						</svg>
					</button>
				</div>
			</div>

			<!-- Font family -->
			<div>
				<span class="mb-1.5 block text-sm text-neutral-600 dark:text-neutral-400">Font</span>
				<div class="flex gap-1">
					{#each fonts as font}
						<button
							onclick={() => setFont(font.value)}
							class="flex-1 rounded-md px-2 py-1.5 text-xs font-medium transition-colors"
							class:bg-blue-100={preferences.articleFont === font.value}
							class:text-blue-700={preferences.articleFont === font.value}
							class:dark:bg-blue-900={preferences.articleFont === font.value}
							class:dark:text-blue-300={preferences.articleFont === font.value}
							class:hover:bg-neutral-100={preferences.articleFont !== font.value}
							class:dark:hover:bg-neutral-800={preferences.articleFont !== font.value}
						>
							{font.label}
						</button>
					{/each}
				</div>
			</div>
		</div>
	{/if}
</div>
