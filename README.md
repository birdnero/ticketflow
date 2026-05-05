# TicketFlow Static Web Prototype

## Project overview

TicketFlow is a static front-end prototype for a commercial event ticketing platform.
It includes account operations, event discovery, seat reservation, checkout, and session logout flows.

## Screens

- `src/index.html` - product overview and navigation hub
- `src/html/login.html` - secure sign-in with validation messaging
- `src/html/profile.html` - personal profile editing (vip), contact details, and password update flow
- `src/html/user-info.html` - selected user profile and activity timeline
- `src/html/user-edit.html` - user profile editing with validation and notifications
- `src/html/events.html` - event catalog
- `src/html/event-ticket.html` - seat map with availability states and booking actions
- `src/html/reservations.html` - reservation and purchase history
- `src/html/checkout.html` - payment and confirmation flow
- `src/html/logout.html` - sign-out confirmation state

## Styling architecture

- `styles/_variables.scss` - global design tokens and color variables
- `styles/_mixins.scss` - reusable mixins
- `styles/_base.scss` - layout, typography, and shared page structure
- `styles/_components.scss` - buttons, forms, alerts, tables, and status components
- `styles/_pages.scss` - page-level visuals
- `styles/main.scss` - SCSS entry point
- `src/css/main.css` - compiled CSS used by the HTML pages

## Build CSS

```bash
npx --yes sass styles/main.scss src/css/main.css --style=expanded --no-source-map
```

Start with `src/index.html`.
