<script lang="ts">
	interface Props {
		date: string;
	}

	let { date }: Props = $props();

	let formatted = $derived(() => {
		const now = Date.now();
		const then = new Date(date).getTime();
		const diff = now - then;
		const minutes = Math.floor(diff / 60000);
		const hours = Math.floor(diff / 3600000);
		const days = Math.floor(diff / 86400000);

		if (minutes < 1) return 'just now';
		if (minutes < 60) return `${minutes}m ago`;
		if (hours < 24) return `${hours}h ago`;
		if (days < 7) return `${days}d ago`;
		return new Date(date).toLocaleDateString();
	});
</script>

<time datetime={date} title={new Date(date).toLocaleString()}>
	{formatted()}
</time>
