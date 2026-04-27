# crofAI UI

HTML/CSS/JS UI for [crof.ai](https://crof.ai).

## Usage

Serve the files with any static file server, or open `home.html` directly in a browser. No build step needed.

Some pages expect Jinja2 template variables (passed by the Python backend at `crof.ai`). They'll still render as static HTML — the template tags just won't be populated.

## Structure

```
├── home.html           landing page
├── playground.html     main AI chat interface
├── dashboard.html      user dashboard / API keys
├── pricing.html        subscription plans
├── settings.html       account settings
├── docs.html           documentation
├── dedicated.html      dedicated deployment management
├── signin / signup     auth pages
├── crofui.css          global styles
├── crofui.js           global scripts
└── *.html              legal / misc pages
```

## Contributing

Open a PR. Keep it focused — this is a UI-only repo.
