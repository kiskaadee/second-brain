---
type: plan
status: completed
project: bdinvite
tags:
  - bdinvite
  - frontend
  - react
  - design
  - specifications
---

# Digital Invitation — Frontend Specification

## 1. Purpose

A responsive, mobile-first digital birthday invitation that reproduces the visual character of a physical invitation while adding an interactive RSVP flow.

The application has two distinct experiences:

### Guest experience

A highly designed invitation consisting of:

1. Invitation cover
    
2. RSVP call-to-action
    
3. RSVP form
    
4. Submission feedback
    
5. Optional event/location information
    

### Admin experience

A simple dashboard allowing the event organizer to:

- authenticate
    
- view people who have responded
    
- inspect RSVP information
    
- distinguish successful registrations from other states
    
- optionally export or manage responses
    

The guest experience is the primary design focus. The admin dashboard deliberately does **not** need the invitation's visual effects.

---

# 2. Design Principles

The frontend should follow five principles.

### 2.1 The invitation is a physical object

The invitation maintains a fixed vertical aspect ratio regardless of viewport width.

The browser provides a responsive **stage** around it.

```text
Desktop

┌────────────────────────────────────────────┐
│                                            │
│          ┌──────────────────┐              │
│          │                  │              │
│          │   INVITATION     │              │
│          │                  │              │
│          │                  │              │
│          └──────────────────┘              │
│                                            │
└────────────────────────────────────────────┘
```

On mobile, the invitation expands to occupy the available width.

---

### 2.2 One visual composition

There should not be separate mobile and desktop invitation designs.

The same invitation is scaled responsively.

Desktop provides additional surrounding space; mobile provides essentially the entire viewport to the invitation.

---

### 2.3 Decoration must not interfere with information

The animated particle background is subordinate to the content.

Particles should:

- concentrate toward the upper-left and lower-right
    
- remain sparse around the central content
    
- move slowly
    
- vary in size and opacity
    
- have soft golden glows
    
- occasionally pulse subtly
    
- never make text difficult to read
    

The central diagonal/content region should remain substantially darker.

---

### 2.4 The RSVP interaction is part of the invitation

The form should not look like an unrelated web application.

It inherits:

- background
    
- typography
    
- spacing
    
- color
    
- particle atmosphere
    
- restrained visual language
    

The admin dashboard is exempt from this constraint.

---

### 2.5 Content is configuration, not code

Event-specific copy must not be hardcoded into components.

The frontend should be capable of rendering a different invitation by changing configuration.

For example:

```text
Birthday Party
You're Invited
Isabelle Snow
October 28
7:00 PM
```

should be data rather than component markup.

---

# 3. Guest Experience

## State 1 — Invitation

The initial viewport displays the invitation.

Conceptually:

```text
┌─────────────────────────────┐
│                             │
│       BIRTHDAY PARTY        │
│                             │
│       YOU'RE INVITED        │
│                             │
│        ISABELLE SNOW        │
│                             │
│         OCT 28              │
│         7:00 PM             │
│                             │
│                             │
│   CONFIRMA TU ASISTENCIA    │
│              ↓              │
│                             │
└─────────────────────────────┘
```

The actual visual hierarchy should use the previously established typography system:

- script/display font for major handwritten elements
    
- Montserrat or equivalent geometric sans-serif for metadata
    
- uppercase + generous tracking for supporting information
    

The address is deliberately omitted from the front.

Instead, its position becomes the RSVP CTA.

---

# 4. RSVP CTA

The CTA should be visually integrated into the invitation.

Default copy:

> **CONFIRMA TU ASISTENCIA**  
> ↓

The entire CTA region should be interactive.

Interaction:

```text
click CTA
    ↓
smooth transition
    ↓
RSVP section
```

The CTA should also be keyboard accessible and have a visible focus state.

The arrow is decorative but should not be the only indication that the element is interactive.

---

# 5. RSVP Form

The form appears below the invitation.

Conceptually:

```text
┌─────────────────────────────┐
│                             │
│        ¿NOS VEMOS?          │
│                             │
│   NOMBRE COMPLETO           │
│   ─────────────────────     │
│                             │
│   TELÉFONO                  │
│   ─────────────────────     │
│                             │
│   CORREO · OPCIONAL         │
│   ─────────────────────     │
│                             │
│        TE VEO AHÍ           │
│                             │
└─────────────────────────────┘
```

### Fields

#### Full name

Required.

```text
name
```

Validation:

- non-empty
    
- reasonable maximum length
    
- whitespace normalized
    

#### Phone

Required.

```text
phone
```

The frontend should perform basic format validation but should **not assume a specific international phone-number format unless the event requires one**.

#### Email

Optional.

```text
email
```

If provided, it should be validated as an email address.

The frontend should not make email mandatory simply because the backend can store it.

---

# 6. Submit Button

Default:

> **TE VEO AHÍ**

The wording is configurable.

Other possible configured values could include:

```text
TE VEO AHÍ
NOS VEMOS
AHÍ ESTARÉ
CONFIRMAR ASISTENCIA
```

The component should not care which copy is selected.

---

# 7. Form Validation

Validation should happen before submission.

For example:

```text
NOMBRE COMPLETO
[                       ]

Este campo es obligatorio.
```

Errors should appear close to the relevant field.

Avoid browser-default validation messages as the primary experience.

The visual treatment should remain consistent with the invitation.

The form should not clear valid fields merely because one field failed validation.

---

# 8. Submission State

After the user submits:

```text
form
  ↓
submitting
```

The button enters a loading state.

For example:

```text
ENVIANDO...
```

The user should not be able to submit the same form repeatedly while the request is in progress.

This state is particularly important because the backend may take longer than expected.

---

# 9. Successful Submission

The backend returns a semantic success response.

The frontend transitions to:

```text
┌─────────────────────────────┐
│                             │
│          ¡PERFECTO!         │
│                             │
│   Tu asistencia ha sido     │
│        confirmada.          │
│                             │
│      Gracias, [Nombre].     │
│                             │
│       TE VEO EN 00:00:00    │
│                             │
│       [MAP]           │
│                             │
└─────────────────────────────┘
```

** implementar un counter para la hora y fecha de la fiesta, hora colombia; 

Dirección es un area circular t

Your proposed:

> "Perfecto! Has sido registrado, gracias"

works functionally, but I would make the wording more natural:

> **¡Perfecto! Tu asistencia ha sido confirmada. Gracias.**

Or, more personal:

> **¡Perfecto! Te esperamos. Gracias por confirmar.**

Again, this should be configurable.

The frontend should not infer success from HTTP status alone. The API contract should define a semantic result.

---

# 10. Duplicate Submission

This is an important state.

For example, the backend determines that the phone number or email already corresponds to an RSVP.

The frontend displays:

> **¡UPS!**

> Parece que ya tenemos tus datos registrados.

Potentially:

> Si necesitas modificar tu información, ponte en contacto con nosotros.

I would **not expose which field caused the duplicate** unless there is a reason to do so.

For example, don't necessarily tell the user:

> El correo `foo@example.com` ya está registrado.

That unnecessarily reveals stored information.

The frontend only needs to know:

```text
DUPLICATE_RSVP
```

and render the configured message.

---

# 11. Unexpected Error

The application needs a generic failure state.

For example:

> **ALGO SALIÓ MAL**

> No pudimos registrar tu asistencia. Inténtalo nuevamente.

With:

> **INTENTAR DE NUEVO**

The frontend should distinguish this from validation and duplicate responses.

Conceptually:

```text
VALIDATION_ERROR
        ↓
fix form

DUPLICATE
        ↓
duplicate message

SUCCESS
        ↓
confirmation

SERVER_ERROR
        ↓
retry
```

This separation is important.

---

# 12. Network Failure

A network failure should produce essentially the same user-facing state as an unexpected server failure.

The frontend should not expose:

```text
500 Internal Server Error
SQLite database locked
Connection refused
FastAPI exception
```

Those are implementation details.

Instead:

> **No pudimos comunicarnos con el servidor.**

> Inténtalo nuevamente.

---

# 13. Optional Post-RSVP Information

After successful registration, the application can expose practical information:

```text
¡PERFECTO!

Te esperamos el 28.

FRESCO RISTORANTE
514 S BRAND BLVD.
GLENDALE, CA

[ VER UBICACIÓN ]
```

I would actually put the location **after successful RSVP**, assuming there isn't a reason guests need the address before responding.

This creates a nice information hierarchy:

```text
Invitation
     ↓
RSVP
     ↓
Confirmation
     ↓
Logistics
```

---

# 14. Invitation Configuration

The event-specific content should be represented by configuration.

Conceptually:

```ts
interface InvitationConfig {
    title: string;
    invitationText: string;
    honoree: string;

    date: string;
    time: string;

    rsvp: {
        title: string;
        cta: string;

        fields: {
            name: FieldConfig;
            phone: FieldConfig;
            email: FieldConfig;
        };

        submitLabel: string;
    };

    messages: {
        success: string;
        duplicate: string;
        validation: string;
        error: string;
    };

    location?: {
        name: string;
        address: string;
        mapsUrl?: string;
    };
}
```

The exact implementation language/framework is irrelevant to the specification.

The important requirement is:

**changing event content must not require modifying presentation components.**

---

# 15. Backend Boundary

The frontend should have a very small conceptual API.

For example:

```text
POST /api/rsvp
```

Request:

```json
{
    "name": "...",
    "phone": "...",
    "email": "..."
}
```

The frontend should only care about semantic responses such as:

```text
SUCCESS
DUPLICATE
VALIDATION_ERROR
ERROR
```

It should not know:

```text
SQLite
FastAPI
database schema
database IDs
SQL queries
persistence strategy
```

That gives you the separation you're looking for.

The backend can change from SQLite to PostgreSQL later without requiring the invitation UI to change.

---

# 16. Accessibility Requirements

This is particularly important because the design is highly visual.

The invitation must still work without relying on visual effects.

Requirements:

- semantic HTML
    
- keyboard-accessible CTA
    
- keyboard-accessible form
    
- labels associated with inputs
    
- visible focus states
    
- sufficient text contrast
    
- `aria-live` for submission feedback
    
- reduced-motion support
    
- screen-reader-friendly error messages
    

### Reduced motion

If:

```css
@media (prefers-reduced-motion: reduce)
```

is active:

- disable particle movement
    
- disable particle pulsing
    
- disable elaborate scrolling animation
    
- retain the visual background
    
- allow normal browser scrolling
    

The invitation should remain visually attractive as a static composition.

---

# 17. Particle Background Specification

The background should be implemented independently from the content.

### Particle properties

Each particle may have:

```text
position
radius
opacity
blur
gold intensity
velocity
twinkle speed
twinkle phase
```

### Spatial distribution

High density:

```text
upper-left
lower-right
```

Low density:

```text
central content region
```

### Animation

Movement should be extremely slow.

The goal is:

> "the background is alive"

rather than:

> "there is a particle animation."

The background should never compete with the typography.

---

# 18. Responsive Behavior

The invitation itself maintains its aspect ratio.

Conceptually:

```css
.invitation {
    width: min(100%, 480px);
    aspect-ratio: <design-ratio>;
}
```

Desktop:

```text
             ┌──────────────┐
             │              │
             │ INVITATION   │
             │              │
             └──────────────┘
```

Mobile:

```text
┌────────────────┐
│                │
│  INVITATION    │
│                │
│                │
└────────────────┘
```

The surrounding page/stage adapts to the viewport.

No separate desktop artwork is required.

---

# 19. Admin Dashboard

The dashboard should deliberately be much simpler.

I would **not attempt to reproduce the invitation aesthetic** here.

Something like:

```text
┌──────────────────────────────────────────────────┐
│ RSVP Dashboard                          Log out   │
├──────────────────────────────────────────────────┤
│                                                  │
│  Responses: 37                                   │
│                                                  │
│  Search: [________________________]               │
│                                                  │
│  Name              Phone          Email           │
│  ───────────────────────────────────────────────  │
│  Ana García        300...         ana@...        │
│  Carlos Pérez      311...         —              │
│  María López       315...         maria@...      │
│                                                  │
└──────────────────────────────────────────────────┘
```

### Dashboard capabilities

Minimum viable dashboard:

- authentication
    
- total RSVP count
    
- response table
    
- name
    
- phone
    
- email
    
- submission timestamp
    
- search/filter
    

Potentially later:

- CSV export
    
- delete/cancel RSVP
    
- edit RSVP
    
- attendance status
    
- guest count
    

But those should not be required for v1.

---

# 20. Admin Authentication

Authentication is a backend concern, but the frontend needs to represent:

```text
/login
/dashboard
```

Unauthenticated users attempting to access the dashboard are redirected to login.

The dashboard should not rely on hiding the route as its security mechanism.

The API must enforce authorization independently.

---

# 21. Suggested Application Structure

I would organize the frontend conceptually like this:

```text
src/
├── invitation/
│   ├── Invitation.tsx
│   ├── InvitationContent.tsx
│   ├── ParticleBackground.tsx
│   ├── RSVPCTA.tsx
│   ├── RSVPForm.tsx
│   └── RSVPResult.tsx
│
├── admin/
│   ├── Login.tsx
│   ├── Dashboard.tsx
│   └── RSVPTable.tsx
│
├── components/
│   ├── Button.tsx
│   ├── Field.tsx
│   └── ...
│
├── config/
│   └── invitation.ts
│
├── api/
│   └── rsvp.ts
│
└── styles/
    ├── invitation.css
    ├── particles.css
    └── admin.css
```

The exact framework doesn't matter; this is primarily a **separation-of-concerns model**.

---

# 22. Guest State Machine

I would explicitly document this because it gives the frontend implementation a very clear contract:

```text
                 ┌──────────────┐
                 │ INVITATION   │
                 └──────┬───────┘
                        │
                    CTA click
                        │
                        ▼
                 ┌──────────────┐
                 │ RSVP FORM    │
                 └──────┬───────┘
                        │
                    submit
                        │
                        ▼
                 ┌──────────────┐
                 │ SUBMITTING   │
                 └──────┬───────┘
                        │
             ┌──────────┼───────────┐
             │          │           │
             ▼          ▼           ▼
          SUCCESS    DUPLICATE    ERROR
             │          │           │
             ▼          ▼           ▼
          RESULT      RESULT      RESULT
```

Validation occurs before `SUBMITTING`:

```text
RSVP FORM
   │
   ├── invalid → validation errors
   │
   └── valid → SUBMITTING
```

This is probably the most important functional artifact in the specification because it makes the frontend/backend boundary explicit.

---

# 23. Things I Think We're Now Missing

There are only a few things I'd decide before implementation.

### 1. What happens after successful RSVP?

I recommend:

**confirmation + event information + location link**

rather than simply showing "thanks."

### 2. Can someone change their RSVP?

For v1, I'd say **no** unless there is a concrete requirement.

If someone needs to change their information, provide a contact mechanism rather than building an account system.

### 3. Can someone bring a guest?

This needs to be decided because it fundamentally changes the data model.

If everyone is individually invited, the current form is sufficient.

If:

> "Andrés + 1"

is possible, you'll eventually need a guest-count or companion field.

### 4. Is the phone number actually necessary?

If the host genuinely uses it to coordinate the event, keep it required.

If it's only being collected because "RSVP forms usually ask for phone," I'd reconsider. Collecting less personal information makes the system simpler.

### 5. What does duplicate mean?

I'd define it at the API contract level, for example:

> A submission is considered a duplicate if the normalized phone number already belongs to an existing RSVP, or if a provided email matches an existing RSVP.

The frontend shouldn't implement that logic.

---

# Final product model

The complete experience becomes:

```text
                  GUEST
                    │
                    ▼
          ┌──────────────────┐
          │   INVITATION      │
          │                  │
          │   Birthday       │
          │      Party       │
          │                  │
          │  Isabelle Snow   │
          │                  │
          │    OCT 28        │
          │    7:00 PM       │
          │                  │
          │ CONFIRMA TU       │
          │ ASISTENCIA   ↓   │
          └────────┬─────────┘
                   │
                   ▼
          ┌──────────────────┐
          │    RSVP FORM     │
          │                  │
          │ Nombre           │
          │ Teléfono         │
          │ Email (optional) │
          │                  │
          │   TE VEO AHÍ     │
          └────────┬─────────┘
                   │
                submit
                   │
                   ▼
          ┌──────────────────┐
          │   SUBMITTING     │
          └────────┬─────────┘
                   │
       ┌───────────┼────────────┐
       ▼           ▼            ▼
   SUCCESS      DUPLICATE     ERROR
       │           │            │
       ▼           ▼            ▼
  "¡Perfecto!"  "¡Ups!"     "Algo salió
                             mal"
       │
       ▼
   EVENT INFO
       │
       ▼
  LOCATION / MAP


              ADMIN
                │
                ▼
          ┌─────────────┐
          │    LOGIN    │
          └──────┬──────┘
                 ▼
          ┌─────────────┐
          │  DASHBOARD  │
          │             │
          │ 37 RSVPs    │
          │             │
          │ Name        │
          │ Phone       │
          │ Email       │
          │ Timestamp   │
          └─────────────┘
```

