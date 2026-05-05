const API_BASE = 'http://127.0.0.1:8001';

const byId = (id) => document.getElementById(id);

const resolveBannerUrl = (value) => {
    if (!value) {
        return value;
    }

    if (/^(?:https?:|data:|blob:|\/)/.test(value)) {
        return value;
    }

    const normalized = value.replace(/^\.\//, '');
    const isHtmlPage = window.location.pathname.includes('/html/');
    return isHtmlPage ? `../${normalized}` : normalized;
};

const fetchJson = async (path) => {
    const response = await fetch(`${API_BASE}${path}`, {
        headers: {
            Accept: 'application/json',
        },
    });

    if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
    }

    return response.json();
};

const formatDateTime = (value) => {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return date.toLocaleString('en-GB', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
    });
};

const formatDate = (value) => {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return date.toLocaleDateString('en-CA');
};

const setText = (el, text) => {
    const target = el;
    if (target) {
        target.textContent = text;
    }
};

const buildEventCard = (event) => {
    const article = document.createElement('article');
    article.className = 'event-card';

    const banner = document.createElement('div');
    banner.className = 'event-banner';
    if (event.banner_url) {
        banner.style.backgroundImage = `url(${resolveBannerUrl(event.banner_url)})`;
    }

    const body = document.createElement('div');
    body.className = 'event-body stack-block';

    const title = document.createElement('h2');
    title.className = 'event-title';
    title.textContent = event.title;

    const meta = document.createElement('p');
    meta.className = 'event-meta';
    meta.textContent = `${event.venue} · ${formatDateTime(event.starts_at)}`;

    const chips = document.createElement('ul');
    chips.className = 'info-chip-list';

    const chipCategory = document.createElement('li');
    chipCategory.className = 'info-chip';
    chipCategory.textContent = event.category;

    const chipCity = document.createElement('li');
    chipCity.className = 'info-chip';
    chipCity.textContent = event.city;

    const chipPrice = document.createElement('li');
    chipPrice.className = 'info-chip';
    chipPrice.textContent = `from $${event.base_price.toFixed(2)}`;

    chips.append(chipCategory, chipCity, chipPrice);

    const link = document.createElement('a');
    link.className = 'btn btn-primary';
    link.href = `event-ticket.html?event=${event.id}`;
    link.textContent = 'view seats';

    body.append(title, meta, chips, link);
    article.append(banner, body);

    return article;
};

const renderEvents = async () => {
    const grid = byId('events-grid');
    if (!grid) {
        return;
    }

    try {
        const events = await fetchJson('/events');
        grid.innerHTML = '';
        events.forEach((event) => {
            grid.append(buildEventCard(event));
        });
    } catch (err) {
        return err;
    }
};

const flattenSeats = (seatMap) => {
    if (!seatMap || !Array.isArray(seatMap.sections)) {
        return [];
    }

    const seats = [];
    seatMap.sections.forEach((section) => {
        if (!section || !Array.isArray(section.rows)) {
            return;
        }
        section.rows.forEach((row) => {
            if (!row || !Array.isArray(row.seats)) {
                return;
            }
            row.seats.forEach((seat) => {
                seats.push(seat);
            });
        });
    });

    return seats;
};

const renderEventTicket = async () => {
    const seatGrid = byId('seat-grid');
    if (!seatGrid) {
        return;
    }

    const params = new URLSearchParams(window.location.search);
    const eventId = params.get('event') || '1';

    try {
        const event = await fetchJson(`/events/${eventId}`);
        setText(byId('map-title'), `${event.title} · ${event.venue}`);
        setText(byId('event-subtitle'), event.description);

        const seats = flattenSeats(event.seat_map);
        seatGrid.innerHTML = '';
        seats.forEach((seat) => {
            const span = document.createElement('span');
            span.className = 'ticket-seat';
            if (seat.status === 'reserved') {
                span.classList.add('is-reserved');
            } else if (seat.status === 'blocked') {
                span.classList.add('is-sold');
            } else {
                span.classList.add('is-available');
            }
            span.setAttribute('role', 'listitem');
            span.textContent = seat.id;
            seatGrid.append(span);
        });

        const firstAvailable = seats.find((seat) => seat.status === 'available') || seats[0];
        if (firstAvailable) {
            setText(byId('selected-seat'), firstAvailable.id);
        }
        setText(byId('seat-price'), `$${event.base_price.toFixed(2)}`);
    } catch (err) {
        return err;
    }
};

const renderReservations = async () => {
    const list = byId('reservation-list');
    if (!list) {
        return;
    }

    try {
        const reservations = await fetchJson('/users/1/reservations');
        list.innerHTML = '';

        let activeCount = 0;
        let paidCount = 0;
        let cancelledCount = 0;

        reservations.forEach((reservation) => {
            const item = document.createElement('li');
            item.className = 'timeline-item';

            const top = document.createElement('div');
            top.className = 'timeline-top';

            const title = document.createElement('h3');
            title.className = 'timeline-title';
            title.textContent = `${reservation.event_title} · seat ${reservation.seats.join(', ')}`;

            const badge = document.createElement('span');
            badge.className = 'status-badge';

            if (reservation.status === 'confirmed') {
                badge.classList.add('is-paid');
                badge.textContent = 'paid';
                paidCount += 1;
            } else if (reservation.status === 'pending') {
                badge.classList.add('is-reserved');
                badge.textContent = 'reserved';
                activeCount += 1;
            } else {
                badge.classList.add('is-cancelled');
                badge.textContent = 'cancelled';
                cancelledCount += 1;
            }

            top.append(title, badge);

            const meta = document.createElement('p');
            meta.className = 'timeline-meta';
            meta.textContent = `${formatDateTime(reservation.created_at)} · total $${reservation.total_amount.toFixed(2)}`;

            item.append(top, meta);
            list.append(item);
        });

        setText(byId('summary-active'), String(activeCount));
        setText(byId('summary-paid'), String(paidCount));
        setText(byId('summary-cancelled'), String(cancelledCount));
    } catch (err) {
        return err;
    }
};

const renderProfile = async () => {
    const profileName = byId('profile-display-name');
    if (!profileName) {
        return;
    }

    try {
        const user = await fetchJson('/users/1');
        setText(byId('vip-tier'), user.vip_tier ? user.vip_tier.toLowerCase() : 'standard');

        profileName.value = user.full_name || '';
        const email = byId('profile-email');
        if (email) {
            email.value = user.email || '';
        }
        const phone = byId('profile-phone');
        if (phone) {
            phone.value = user.phone || '';
        }

        setText(byId('profile-user-id'), `u-${user.id}`);
        setText(byId('profile-member-since'), formatDate(user.created_at));
        setText(byId('profile-last-login'), formatDateTime(user.created_at));
    } catch (err) {
        return err;
    }
};

const renderUserInfo = async () => {
    const userTitle = byId('user-info-title');
    if (!userTitle) {
        return;
    }

    try {
        const user = await fetchJson('/users/1');
        setText(userTitle, user.full_name);
        setText(byId('user-info-id'), `u-${user.id}`);
        setText(byId('user-info-email'), user.email);
        setText(byId('user-info-created'), formatDate(user.created_at));
        setText(byId('user-info-last'), formatDateTime(user.created_at));
    } catch (err) {
        return err;
    }
};

const init = () => {
    renderEvents();
    renderEventTicket();
    renderReservations();
    renderProfile();
    renderUserInfo();
};

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
