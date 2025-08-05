# QuickNotes

A simple note-taking app for Frappe Framework with real-time collaboration.

## Features

- Create and edit rich-text notes
- Share notes with other users (Read/Write/Admin permissions)
- Public/private notes
- Real-time collaboration via Socket.io
- Auto-save functionality

## Installation

```bash
# Create new app
bench new-app quicknotes

# Install app
bench --site your-site install-app quicknotes

# Run migrations
bench --site your-site migrate

# Build and restart
bench build
bench restart
```

## Usage

1. Navigate to `/quicknotes` on your site
2. Create new notes or select existing ones
3. Share notes by clicking the Share button
4. Toggle public/private visibility as needed

## File Structure

```
quicknotes/
├── quicknotes/
│   ├── hooks.py
│   ├── api.py
│   ├── www/quicknotes/
│   │   ├── index.py
│   │   └── index.html
│   └── quicknotes/doctype/
│       ├── quick_note/
│       └── quick_note_share/
```

## Requirements

- Frappe Framework v13+
- Socket.io for real-time features

## License

MIT
