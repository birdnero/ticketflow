# TicketFlow Static Web Prototype

## Project overview

TicketFlow is a static front-end prototype for a commercial event ticketing platform.
It includes account operations, event discovery, seat reservation, checkout, and session logout flows.

## Screens

- `index.html` - product overview and navigation hub
- `login.html` - secure sign-in with validation messaging
- `profile.html` - personal profile editing (vip), contact details, and password update flow
- `user-info.html` - selected user profile and activity timeline
- `user-edit.html` - user profile editing with validation and notifications
- `events.html` - event catalog
- `event-ticket.html` - seat map with availability states and booking actions
- `reservations.html` - reservation and purchase history
- `checkout.html` - payment and confirmation flow
- `logout.html` - sign-out confirmation state

## Styling architecture

- `styles/_variables.scss` - global design tokens and color variables
- `styles/_mixins.scss` - reusable mixins
- `styles/_base.scss` - layout, typography, and shared page structure
- `styles/_components.scss` - buttons, forms, alerts, tables, and status components
- `styles/_pages.scss` - page-level visuals
- `styles/main.scss` - SCSS entry point

## Build CSS

```bash
npx --yes sass styles/main.scss css/main.css --style=expanded --no-source-map
```

Start with `index.html`.
