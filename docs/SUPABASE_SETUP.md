# Supabase Setup

## Scope

This guide configures the browser-safe Supabase Auth integration introduced by
`REQ-AUTH-001`. It does not create database tables, service-role credentials,
or production authorization policies.

## 1. Create a Supabase project

1. Sign in to Supabase and create a project.
2. Select a region appropriate for the intended users and data-residency needs.
3. Record the project URL and the browser-safe publishable or anon key.
4. Never copy the service-role key into the frontend or repository.

## 2. Configure local environment values

Copy `.env.example` to `.env.local` and replace the placeholders:

```text
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_PUBLISHABLE_KEY=your-browser-safe-key
```

`.env.local` must remain uncommitted. Vite variables are included in the built
browser bundle, so only values intended for public clients belong there.

## 3. Enable Google authentication

1. Create OAuth credentials in Google Cloud Console.
2. In Supabase Authentication providers, enable Google.
3. Enter the Google client ID and client secret in Supabase, not in the app.
4. Add the Supabase callback URL shown by the provider settings to Google.
5. Restrict OAuth origins and redirect URLs to known development and production
   locations.

## 4. Configure redirect URLs

Add the allowed application URLs in Supabase Authentication URL settings.
Expected examples are:

```text
http://localhost:5173/investment-manager/
https://fiverocksgames.github.io/investment-manager/
```

The deployed URL must be replaced if the canonical repository owner or custom
domain changes. Wildcard redirects should not be used for production unless a
separate security decision approves them.

## 5. Validate

Run the application and verify:

1. Missing environment values show a configuration notice without crashing.
2. Google sign-in redirects only to an allow-listed URL.
3. A successful callback restores the user session.
4. Refreshing the page preserves an active session.
5. Signing out clears the displayed session.
6. Authentication errors are visible without exposing keys or tokens.

Do not claim end-to-end authentication success until these checks are completed
against a real Supabase project.

## Security boundaries

- The project URL and publishable or anon key are browser-safe identifiers, not
  privileged server secrets.
- Service-role keys, database passwords, and Google client secrets never belong
  in Vite variables.
- Authentication proves identity; database authorization must later be enforced
  with Row Level Security.
- No user-owned table may be exposed before its RLS policy and isolation tests
  are reviewed.
