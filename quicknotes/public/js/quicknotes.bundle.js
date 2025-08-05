class QuickNotesApp {
	constructor() {
		this.currentNote = null;
		this.quill = null;
		this.socket = null;
		this.activeUsers = [];
		this.isOwner = false;
		this.canWrite = false;

		this.initializeApp();
	}

	initializeApp() {
		this.loadNotesList();
		this.initializeSocketIO();
		this.bindEvents();
	}

	initializeSocketIO() {
		if (typeof io !== "undefined") {
			this.socket = io();

			this.socket.on("note_updated", (data) => {
				if (data.note_name === this.currentNote && data.user !== frappe.session.user) {
					this.handleRemoteNoteUpdate(data.data);
				}
			});

			this.socket.on("user_joined", (data) => {
				if (data.note_name === this.currentNote) {
					this.handleUserJoined(data);
				}
			});

			this.socket.on("user_left", (data) => {
				if (data.note_name === this.currentNote) {
					this.handleUserLeft(data);
				}
			});
		}
	}

	loadNotesList() {
		frappe.call({
			method: "quicknotes.api.get_my_notes",
			callback: (r) => {
				if (r.message) {
					this.renderNotesList(r.message);
				}
			},
		});
	}

	renderNotesList(notes) {
		const sidebar = document.getElementById("notes-sidebar");
		if (!sidebar) return;

		let html = `
            <div class="notes-header">
                <h3>QuickNotes</h3>
                <button class="btn btn-primary btn-sm" onclick="app.createNewNote()">
                    <i class="fa fa-plus"></i> New Note
                </button>
            </div>
            <div class="notes-sections">
        `;

		// My Notes
		if (notes.owned && notes.owned.length > 0) {
			html += '<div class="notes-section"><h4>My Notes</h4>';
			notes.owned.forEach((note) => {
				html += this.renderNoteItem(note, "owned");
			});
			html += "</div>";
		}

		// Shared Notes
		if (notes.shared && notes.shared.length > 0) {
			html += '<div class="notes-section"><h4>Shared with Me</h4>';
			notes.shared.forEach((note) => {
				html += this.renderNoteItem(note, "shared");
			});
			html += "</div>";
		}

		// Public Notes
		if (notes.public && notes.public.length > 0) {
			html += '<div class="notes-section"><h4>Public Notes</h4>';
			notes.public.forEach((note) => {
				html += this.renderNoteItem(note, "public");
			});
			html += "</div>";
		}

		html += "</div>";
		sidebar.innerHTML = html;
	}

	renderNoteItem(note, type) {
		return `
            <div class="note-item ${this.currentNote === note.name ? "active" : ""}" 
                 onclick="app.openNote('${note.name}')">
                <div class="note-title">${note.title}</div>
                <div class="note-meta">
                    <small>
                        ${type === "owned" ? "by you" : "by " + (note.owner || "Unknown")} • 
                        ${frappe.datetime.comment_when(note.modified)}
                        ${note.is_public ? ' • <i class="fa fa-globe"></i>' : ""}
                    </small>
                </div>
                ${note.tags ? `<div class="note-tags">${note.tags}</div>` : ""}
            </div>
        `;
	}

	createNewNote() {
		const title = prompt("Enter note title:");
		if (!title) return;

		frappe.call({
			method: "quicknotes.api.create_note",
			args: {
				title: title,
				content: "",
				is_public: 0,
			},
			callback: (r) => {
				if (r.message) {
					this.loadNotesList();
					this.openNote(r.message.name);
				}
			},
		});
	}

	openNote(noteName) {
		if (this.currentNote) {
			this.leaveNoteSession(this.currentNote);
		}

		frappe.call({
			method: "quicknotes.api.get_note",
			args: { note_name: noteName },
			callback: (r) => {
				if (r.message) {
					this.currentNote = noteName;
					this.renderNoteEditor(r.message);
					this.joinNoteSession(noteName);
				}
			},
		});
	}

	renderNoteEditor(noteData) {
		const editor = document.getElementById("note-editor");
		if (!editor) return;

		this.canWrite = noteData.can_write;
		this.isOwner = noteData.owner === frappe.session.user;

		const readonly = !this.canWrite;

		let html = `
            <div class="note-header">
                <div class="note-title-section">
                    <h2 contenteditable="${!readonly}" class="note-title" id="note-title">${
			noteData.title
		}</h2>
                    <div class="note-meta">
                        Last edited by ${
							noteData.last_edited_by
						} on ${frappe.datetime.comment_when(noteData.last_edited_at)}
                    </div>
                </div>
                <div class="note-actions">
                    <div class="active-users" id="active-users"></div>
                    ${
						this.canWrite
							? `
                        <button class="btn btn-sm btn-secondary" onclick="app.shareNote()">
                            <i class="fa fa-share"></i> Share
                        </button>
                    `
							: ""
					}
                    ${
						this.isOwner
							? `
                        <button class="btn btn-sm btn-secondary" onclick="app.togglePublic()">
                            <i class="fa fa-globe"></i> ${
								noteData.is_public ? "Make Private" : "Make Public"
							}
                        </button>
                    `
							: ""
					}
                </div>
            </div>
            <div class="note-content">
                <div id="quill-editor"></div>
            </div>
        `;

		editor.innerHTML = html;

		// Initialize Quill editor
		this.initializeQuillEditor(noteData, readonly);

		// Update active users
		this.updateActiveUsers(noteData.active_users || []);

		// Join socket room
		if (this.socket) {
			this.socket.emit("join", `note:${this.currentNote}`);
		}
	}

	initializeQuillEditor(noteData, readonly) {
		const toolbarOptions = readonly
			? false
			: [
					["bold", "italic", "underline", "strike"],
					["blockquote", "code-block"],
					[{ header: 1 }, { header: 2 }],
					[{ list: "ordered" }, { list: "bullet" }],
					[{ script: "sub" }, { script: "super" }],
					[{ indent: "-1" }, { indent: "+1" }],
					[{ direction: "rtl" }],
					[{ size: ["small", false, "large", "huge"] }],
					[{ header: [1, 2, 3, 4, 5, 6, false] }],
					[{ color: [] }, { background: [] }],
					[{ font: [] }],
					[{ align: [] }],
					["clean"],
					["link", "image"],
			  ];

		this.quill = new Quill("#quill-editor", {
			theme: "snow",
			readOnly: readonly,
			toolbar: toolbarOptions,
			modules: {
				toolbar: toolbarOptions,
			},
		});

		// Set initial content
		if (noteData.content_delta) {
			try {
				const delta = JSON.parse(noteData.content_delta);
				this.quill.setContents(delta);
			} catch (e) {
				this.quill.setText(noteData.content || "");
			}
		} else {
			this.quill.setText(noteData.content || "");
		}

		if (!readonly) {
			// Auto-save on text change
			let saveTimeout;
			this.quill.on("text-change", (delta, oldDelta, source) => {
				if (source === "user") {
					clearTimeout(saveTimeout);
					saveTimeout = setTimeout(() => {
						this.saveNote();
					}, 1000); // Auto-save after 1 second of inactivity
				}
			});
		}

		// Handle title editing
		const titleElement = document.getElementById("note-title");
		if (titleElement && !readonly) {
			titleElement.addEventListener("blur", () => {
				this.saveNote();
			});

			titleElement.addEventListener("keypress", (e) => {
				if (e.key === "Enter") {
					e.preventDefault();
					titleElement.blur();
				}
			});
		}
	}

	saveNote() {
		if (!this.canWrite || !this.quill) return;

		const content = this.quill.getText();
		const contentDelta = JSON.stringify(this.quill.getContents());
		const title = document.getElementById("note-title").textContent;

		frappe.call({
			method: "quicknotes.api.save_note_content",
			args: {
				note_name: this.currentNote,
				content: content,
				content_delta: contentDelta,
			},
			callback: (r) => {
				if (r.message && r.message.success) {
					// Update title if changed
					frappe.call({
						method: "frappe.client.set_value",
						args: {
							doctype: "Quick Note",
							name: this.currentNote,
							fieldname: "title",
							value: title,
						},
					});
				}
			},
		});
	}

	handleRemoteNoteUpdate(data) {
		if (this.quill && !this.quill.hasFocus()) {
			try {
				const delta = JSON.parse(data.content_delta);
				this.quill.setContents(delta, "api");
			} catch (e) {
				// Fallback to text content
				this.quill.setText(data.content, "api");
			}
		}
	}

	shareNote() {
		const userEmail = prompt("Enter user email to share with:");
		if (!userEmail) return;

		const permission = prompt("Enter permission level (Read/Write/Admin):", "Read");
		if (!permission) return;

		frappe.call({
			method: "quicknotes.api.share_note",
			args: {
				note_name: this.currentNote,
				user_email: userEmail,
				permission_level: permission,
			},
			callback: (r) => {
				if (r.message && r.message.success) {
					frappe.show_alert(r.message.message, 5);
				}
			},
		});
	}

	togglePublic() {
		frappe.call({
			method: "frappe.client.get_value",
			args: {
				doctype: "Quick Note",
				name: this.currentNote,
				fieldname: "is_public",
			},
			callback: (r) => {
				const newValue = r.message.is_public ? 0 : 1;

				frappe.call({
					method: "frappe.client.set_value",
					args: {
						doctype: "Quick Note",
						name: this.currentNote,
						fieldname: "is_public",
						value: newValue,
					},
					callback: () => {
						this.openNote(this.currentNote); // Refresh the editor
					},
				});
			},
		});
	}

	joinNoteSession(noteName) {
		frappe.call({
			method: "quicknotes.api.join_note_session",
			args: { note_name: noteName },
		});
	}

	leaveNoteSession(noteName) {
		frappe.call({
			method: "quicknotes.api.leave_note_session",
			args: { note_name: noteName },
		});

		if (this.socket) {
			this.socket.emit("leave", `note:${noteName}`);
		}
	}

	handleUserJoined(data) {
		if (!this.activeUsers.find((u) => u.user === data.user)) {
			this.activeUsers.push({
				user: data.user,
				user_full_name: data.user_full_name,
			});
			this.updateActiveUsers(this.activeUsers);
		}
	}

	handleUserLeft(data) {
		this.activeUsers = this.activeUsers.filter((u) => u.user !== data.user);
		this.updateActiveUsers(this.activeUsers);
	}

	updateActiveUsers(users) {
		this.activeUsers = users;
		const container = document.getElementById("active-users");
		if (!container) return;

		let html = "";
		users.forEach((user) => {
			if (user.user !== frappe.session.user) {
				html += `<span class="active-user-badge" title="${
					user.user_full_name || user.user
				}">
                    ${(user.user_full_name || user.user).charAt(0).toUpperCase()}
                </span>`;
			}
		});

		container.innerHTML = html;
	}

	bindEvents() {
		// Handle page unload
		window.addEventListener("beforeunload", () => {
			if (this.currentNote) {
				this.leaveNoteSession(this.currentNote);
			}
		});

		// Handle keyboard shortcuts
		document.addEventListener("keydown", (e) => {
			if (e.ctrlKey || e.metaKey) {
				if (e.key === "s") {
					e.preventDefault();
					this.saveNote();
				}
			}
		});
	}
}

// Initialize app when DOM is ready
document.addEventListener("DOMContentLoaded", function () {
	if (window.location.pathname.includes("/quicknotes")) {
		window.app = new QuickNotesApp();
	}
});
