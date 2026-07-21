# Main menu and buttons
btn-profile = 👤 My Profile
btn-catalog = 📂 Catalog
btn-support = ✍️ Write to Nihao-chan (Support)
btn-admin = ⚙️ Admin Panel
btn-cancel = ❌ Cancel
btn-back-to-menu = 🔙 Main Menu
btn-back-to-catalog = 🔙 Back to Catalog
btn-admin-stats = 📊 Statistics
btn-admin-mailing = 📣 Create Broadcast
btn-admin-users = 👥 User Management
btn-admin-panel = 🔙 Control Panel
btn-admin-logs = 📋 Get Logs
btn-admin-tickets = 📬 Tickets ({ $count })
admin-tickets-empty = 📭 All user tickets are closed or empty.
admin-tickets-title =
    📬 **Ticket #{ $id }** [{ $status }]
    
    👤 **Sender:** { $name } (ID: <code>{ $user_id }</code>, @{ $username })
    📅 **Created At:** { $date }
    
    💬 **Message:**
    <code>{ $message }</code>
btn-ticket-close = ❌ Close Ticket
btn-ticket-prev = ⬅️ Prev
btn-ticket-next = Next ➡️

# Errors and limitations
err-banned-message =
    Unfortunately, you are banned in the Nihao-chan system. ❌
    Contact support if this is a mistake.
err-banned-callback = You are banned! Access denied.
err-no-users = There are no registered users in the database.
err-self-ban = You cannot ban yourself!
err-ban-admin = You cannot ban another administrator!
err-invalid-tg-id = Error! Telegram ID must consist of digits only. Try again:
err-user-not-found = User with ID { $id } was not found in the bot's database.
err-ticket-length =
    Support ticket description must be from 10 to 1000 characters.
    Please formulate your question correctly.
err-item-not-found = Unfortunately, this style was not found.
err-logs-not-found = ❌ Log file not found on the server.

# Welcomes
welcome-text-start =
    Nihao, { $name }! 🌸
    I am Nihao-chan, your interactive assistant.
    
    Glad to see you! How can I help you today?
help-text =
    Available commands:
    | /start - Launch the bot and enter menu
    | /help - Show list of commands
    | /about - About Nihao-chan
help-text-admin =
    | /admin - Enter the administrator panel
about-text =
    ✨ **Nihao-chan Bot** is a high-quality Telegram bot boilerplate,
    built on the Aiogram 3.x framework and SQLAlchemy 2.0 Async database.
    
    The boilerplate supports role model (user/admin), FSM states, anti-flood protection, and SQLite/PostgreSQL database.
menu-title =
    Nihao-chan Main Menu 🌸
    Select the section you are interested in:

# Profile
profile-title =
    👤 **Nihao-chan Profile**
    
    ┣ **Name:** { $name }
    ┣ **Username:** { $username }
    ┣ **Telegram ID:** `{ $id }`
    ┣ **Role:** `{ $role }`
    ┣ **Active Style:** { $theme }
    ┗ **Registration Date:** { $date }
profile-username-empty = not set

# Support (Tickets)
support-prompt =
    ✍️ **Contacting Nihao-chan**
    
    Describe your issue or ask your question in one message.
    We will try to reply as soon as possible!
support-cancel = Sending ticket cancelled.
support-success =
    ✅ **Ticket #{ $id } sent successfully!**
    
    Nihao-chan received your message. We will contact you soon!

# Catalog
catalog-title =
    📂 **Nihao-chan Styles Catalog**
    
    Select the style you want to view details for:
catalog-item-detail =
    🌸 **{ $title }**
    
    📝 **Description:** { $description }
    
    📊 **Rating:** { $rating }

btn-catalog-select = 🌟 Apply Style
catalog-theme-applied = Style "{ $theme }" has been successfully applied!

# Admin Panel
admin-panel-title =
    ⚙️ **Nihao-chan Control Panel**
    
    Logged in with admin rights. Select an action:
admin-stats-title =
    📊 **Nihao-chan Bot Statistics**
    
    ┣ Total users in DB: `{ $total }`
    ┣ Banned users: `{ $banned }`
    ┗ Open support tickets: `{ $tickets }`
admin-mailing-prompt =
    📣 **Create Mass Broadcast**
    
    Send the message (text, photo, video, or sticker) you want to broadcast to all bot users:
admin-mailing-cancel = Broadcast cancelled.
admin-mailing-sending = ⏳ Broadcast started, please wait...
admin-mailing-success =
    📊 **Broadcast finished!**
    
    ┣ Successfully sent: `{ $success }`
    ┗ Sending errors (bot blocked): `{ $failed }`
admin-users-prompt =
    👥 **User Access Management**
    
    Send the Telegram ID of the user you want to ban or unban:
admin-users-cancel = Action cancelled.
admin-users-status-changed = User { $name } (`{ $id }`) is now **{ $status }**.
admin-users-banned = banned ❌
admin-users-unbanned = unbanned  active
admin-logs-caption = 📄 Current bot log file

# Language buttons
btn-lang-ru = 🇷🇺 Русский
btn-lang-en = 🇬🇧 English
lang-select-prompt = Выберите язык интерфейса / Select your language:
lang-changed = Язык интерфейса успешно изменен! / Interface language has been changed!

# Catalog Items
catalog-classic-title = 🌸 Nihao-chan Classic
catalog-classic-desc = Standard Nihao-chan theme. Loves green tea, polite and always ready to help you with code.
catalog-sakura-title = 💮 Nihao-chan Sakura
catalog-sakura-desc = Spring gentle Nihao-chan theme. Surrounded by sakura petals and inspires to write beautiful software.
catalog-cyberpunk-title = ⚡ Nihao-chan Cyberpunk
catalog-cyberpunk-desc = Neon hacker Nihao-chan theme. Writes scripts in assembler, wears cyberimplants and listens to synthwave.
