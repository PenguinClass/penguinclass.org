# penguinclass.org

International Penguin Class Dinghy Association website (Jekyll) with a full legacy archive redirect via 404.

## Quick start
```bash
git clone https://github.com/penguinclass/penguinclass.org.git
cd penguinclass.org
bundle install
bundle exec jekyll serve
```

## Archive workflow
1. Mirror `penguinclass.com` locally (see `archive/README.md`).
2. Copy mirrored files into `archive/` preserving structure.
3. Build manifest:
```bash
python3 scripts/build_archive_manifest.py archive
```
4. Commit and push.

## Analytics (GA4 and Plausible)

Configuration lives under the top-level `analytics` key in [`_config.yml`](_config.yml). Both providers are **off by default** (`enabled: false`), including when you run `bundle exec jekyll serve` (development), so local builds do not send data unless you turn them on.

### What to set in `_config.yml`

- **GA4:** set `analytics.ga4.enabled` to `true` and `analytics.ga4.measurement_id` to your `G-XXXXXXXXXX` ID.
- **Plausible:** set `analytics.plausible.enabled` to `true`, `analytics.plausible.domain` to the site hostname you configured in Plausible (e.g. `penguinclass.org`), and optionally `analytics.plausible.script_src` (defaults to `https://plausible.io/js/script.js`; use your self-hosted script URL if applicable).

Leave any provider disabled or omit IDs/domains to **inject no scripts** for that provider.

### Environment variable overrides (CI / local)

When Jekyll runs with **local plugins enabled** (this repo’s GitHub Actions build uses `bundle exec jekyll build` without safe mode, so `_plugins/` runs), you can override or supply values from the environment:

| Variable | Effect |
|----------|--------|
| `JEKYLL_ANALYTICS_GA4_MEASUREMENT_ID` or `GA4_MEASUREMENT_ID` | Sets GA4 measurement ID |
| `JEKYLL_ANALYTICS_GA4_ENABLED` or `GA4_ANALYTICS_ENABLED` | `true` / `false` (or `1` / `0`) overrides `analytics.ga4.enabled` |
| `JEKYLL_ANALYTICS_PLAUSIBLE_DOMAIN` or `PLAUSIBLE_DOMAIN` | Sets Plausible `data-domain` |
| `JEKYLL_ANALYTICS_PLAUSIBLE_SCRIPT_SRC` or `PLAUSIBLE_SCRIPT_SRC` | Overrides script URL |
| `JEKYLL_ANALYTICS_PLAUSIBLE_ENABLED` or `PLAUSIBLE_ANALYTICS_ENABLED` | Overrides `analytics.plausible.enabled` |

**GitHub Actions:** add repository secrets if you prefer not to commit IDs, then pass them as `env` on the Jekyll build step (see [workflow file](.github/workflows/pages.yml)). You still need `enabled: true` in `_config.yml` unless you also set the corresponding `*_ENABLED` env var.

**Jekyll safe mode:** if a host runs Jekyll with `safe: true`, local plugins (including env merging) are not loaded—use `_config.yml` only, or an extra config file merged with `jekyll build --config _config.yml,_config.prod.yml` generated in CI.

### Verifying in generated HTML

After `bundle exec jekyll build`, open `_site/index.html` (or any page) and search for `googletagmanager.com/gtag/js` (GA4) and/or `plausible` / your `data-domain` (Plausible). If both are disabled or IDs/domains are empty, those strings should be absent.

Implementation: [`_includes/analytics.html`](_includes/analytics.html) is included from [`_layouts/default.html`](_layouts/default.html) in `<head>`.
