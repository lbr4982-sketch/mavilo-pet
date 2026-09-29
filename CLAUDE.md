# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Mavilo Pet Co. is a custom Shopify Online Store 2.0 theme for a U.S. pet brand that sells printable digital pet-care guides (instant PDF downloads): puppy training, new pet setup, health records, dog grooming, and cat enrichment. Nothing is shipped, so storefront copy should talk about instant download rather than shipping.

This is a classic Shopify theme built with Liquid, JSON templates, CSS, and vanilla JavaScript. Do not introduce React, Vite, Next.js, or a separate build pipeline unless the project direction changes.

## Common commands

Use Shopify CLI from the repository root:

- Preview locally: `shopify theme dev`
- Check theme syntax and Shopify rules: `shopify theme check`
- Push/upload to the connected store: `shopify theme push`
- Pull store theme changes into this directory: `shopify theme pull`
- Package the theme for upload: `shopify theme package`

There is no Node package manifest or automated unit test suite in this repository currently. Validation is via Shopify Theme Check and Shopify CLI preview/upload.

## Architecture

- `layout/theme.liquid` is the global shell. It loads `assets/theme.css`, `assets/theme.js`, Shopify `content_for_header`, the header/footer section groups, and the cart drawer container.
- `templates/*.json` are OS 2.0 JSON templates that compose sections for home, product, collection, cart, search, blog, article, page, 404, and customer account pages.
- `sections/*.liquid` contain editable storefront sections and main template sections. Home page merchandising is assembled from `hero`, `category-tiles`, `featured-collection`, `values`, `testimonials`, and `newsletter`.
- `sections/header-group.json` and `sections/footer-group.json` define the global header and footer groups referenced by the layout.
- `snippets/` contains reusable Liquid fragments for product cards, price rendering, quantity input, and social links.
- `assets/theme.css` is the single theme stylesheet. It uses CSS variables populated from theme settings for brand color and typography.
- `assets/theme.js` is vanilla JavaScript for mobile navigation, quantity controls, AJAX add-to-cart, and cart drawer refresh.
- `config/settings_schema.json` defines editor-facing theme settings for logo, favicon, announcement, colors, typography, and cart drawer behavior.
- `locales/en.default.json` contains translation strings used by Liquid templates.

## Business content

- `business/` holds non-theme content: product PDFs and their HTML sources (`business/products/`), a Shopify product import CSV, blog posts, and marketing plans. It is excluded from theme uploads via `.shopifyignore`.

## Theme conventions

- Keep this as a Shopify OS 2.0 theme: add new page layouts as JSON templates plus Liquid sections.
- Prefer editable schema settings and presets for merchant-manageable content.
- Keep JavaScript framework-free; use progressive enhancement and Shopify AJAX endpoints where needed.
- Use Shopify Liquid objects and filters directly rather than generated data layers.
