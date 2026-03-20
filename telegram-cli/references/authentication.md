# Authentication & Sessions

## First-time login

Login is interactive and requires a TTY terminal:

```bash
tg auth login
```

The flow:
1. Prompts for phone number (with country code, e.g., `+1234567890`)
2. Sends SMS/Telegram code
3. Prompts for the code
4. If 2FA is enabled, prompts for password
5. Saves session to disk

**Important:** Claude Code cannot perform interactive login. The user must run `tg auth login` manually first.

## Check auth status

```bash
tg auth status
```

Returns the current user ID and username if logged in, or an error if not.

## Session portability

Export a session for use in another environment (CI, server, another machine):

```bash
# Export
tg session export
# Output: base64-encoded session string

# Import on another machine
tg session import "1BAAOM..."

# Import from stdin (pipe from secret manager, etc.)
echo "$TG_SESSION" | tg session import

# Import without verifying connection (offline)
tg session import "1BAAOM..." --skip-verify
```

## Multi-profile support

Run multiple Telegram accounts side by side:

```bash
# Default profile
tg auth login
tg chat list

# Named profile
tg auth login --profile work
tg chat list --profile work

# Another profile
tg auth login --profile personal
tg message send @friend "Hi" --profile personal
```

Profiles store separate sessions and config. Default profile name is `"default"`.

## Credentials

The CLI needs `TG_API_ID` and `TG_API_HASH` from https://my.telegram.org/apps.

Resolution order:
1. Environment variables: `TG_API_ID`, `TG_API_HASH`
2. Config file: `~/.config/telegram-cli/config.json`
3. Custom config: `--config /path/to/config.json`

## Logout

```bash
tg auth logout
```

Destroys the session on Telegram's servers and removes local session data.
