function emailApp() {
    return {
        emails: [],
        searchQuery: '',
        selectedEmail: null,
        syncing: true,        // For the 500-email list sync
        loadingDetails: false, // For fetching specific body/attachments
        socket: null,

        filteredEmails() {
            if (!this.searchQuery) return this.emails;
            const query = this.searchQuery.toLowerCase();
            return this.emails.filter(e =>
                e.subject.toLowerCase().includes(query) ||
                e.name.toLowerCase().includes(query) ||
                e.from.toLowerCase().includes(query) ||
                (e.snippet && e.snippet.toLowerCase().includes(query))
            );
        },

        initWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
            this.socket = new WebSocket(protocol + window.location.host + '/ws/emails/');

            this.socket.onmessage = (e) => {
                const data = JSON.parse(e.data);

                // Handle the initial list of 500 snippets
                if (data.type === 'list') {
                    this.emails = data.emails;
                    this.syncing = false;
                }
                // Handle the full details of a clicked email
                else if (data.type === 'details') {
                    if (this.selectedEmail && this.selectedEmail.id === data.email_id) {
                        this.selectedEmail.body = data.body;
                        this.selectedEmail.attachments = data.attachments;
                        this.loadingDetails = false;
                    }
                }
            };

            this.socket.onclose = () => {
                setTimeout(() => this.initWebSocket(), 3000);
            };
        },

        selectEmail(email) {
            this.selectedEmail = email;
            // Only fetch details if we haven't loaded them yet
            if (!email.body) {
                this.loadingDetails = true;
                this.socket.send(JSON.stringify({
                    'action': 'get_details',
                    'email_id': email.id
                }));
            }
        },

        refresh() {
            this.syncing = true;
            if (this.socket) {
                this.socket.send(JSON.stringify({ 'action': 'refresh' }));
            }
        },

        formatTime(timeStr) {
            if (!timeStr) return '';
            const date = new Date(timeStr);
            const now = new Date();
            if (date.toDateString() === now.toDateString()) {
                return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            }
            return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
        }
    }
}