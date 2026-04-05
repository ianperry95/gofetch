/**
 * SSE client for real-time updates from the API.
 * Provides reactive state for new article counts and cluster refresh signals.
 */

class LiveUpdatesStore {
	newArticleCount: number = $state(0);
	clustersUpdated: boolean = $state(false);
	connected: boolean = $state(false);

	private eventSource: EventSource | null = null;
	private reconnectTimer: ReturnType<typeof setTimeout> | null = null;

	connect() {
		if (typeof window === 'undefined' || this.eventSource) return;

		this.eventSource = new EventSource('/api/events');

		this.eventSource.onopen = () => {
			this.connected = true;
		};

		this.eventSource.addEventListener('new_entries', (e) => {
			try {
				const data = JSON.parse(e.data);
				this.newArticleCount += data.count || 0;
			} catch {
				// ignore malformed data
			}
		});

		this.eventSource.addEventListener('clusters_updated', () => {
			this.clustersUpdated = true;
		});

		this.eventSource.onerror = () => {
			this.connected = false;
			this.disconnect();
			// Reconnect after 5 seconds
			this.reconnectTimer = setTimeout(() => this.connect(), 5000);
		};
	}

	disconnect() {
		if (this.eventSource) {
			this.eventSource.close();
			this.eventSource = null;
		}
		if (this.reconnectTimer) {
			clearTimeout(this.reconnectTimer);
			this.reconnectTimer = null;
		}
		this.connected = false;
	}

	dismissNewArticles() {
		this.newArticleCount = 0;
	}

	dismissClustersUpdated() {
		this.clustersUpdated = false;
	}
}

export const liveUpdates = new LiveUpdatesStore();
