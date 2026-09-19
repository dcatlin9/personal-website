# dancatlin.site

Personal site for Dan Catlin, Ph.D. — structural biochemist working in commercial strategy.

Plain static HTML and CSS. No build step, no dependencies, no framework.

```
index.html        the page
styles.css        all styling, including responsive rules
favicon.svg       browser-tab icon
images/           headshot, org logos, photos, and the link-preview card
.nojekyll         tells GitHub Pages to serve files as-is
```

## Preview locally

Open `index.html` directly in a browser, or serve it:

```bash
python3 -m http.server 8000   # then visit http://localhost:8000
```

## Publish on GitHub Pages

1. Create a new repository on GitHub. Free Pages hosting requires it to be **public**.
   Note that `dcatlin9.github.io` is already in use by the blog, so name this one something
   else (`site`, `portfolio`) — it will serve from a subpath until a custom domain is attached.
2. Push:
   ```bash
   git remote add origin https://github.com/<username>/<repo>.git
   git push -u origin main
   ```
3. **Settings → Pages → Build and deployment**: Source "Deploy from a branch",
   branch `main`, folder `/ (root)`. Save.
4. Live at `https://<username>.github.io/<repo>/` within a minute or two.

All asset paths are relative, so the site works correctly whether it is served from a
subpath or from the root of a custom domain. Nothing needs changing between the two.

## Attaching a custom domain

1. Buy the domain (Cloudflare, Namecheap, Porkbun — roughly $10–20/year).
2. At the registrar, point DNS at GitHub Pages:
   - Apex (`example.com`): four `A` records → `185.199.108.153`, `185.199.109.153`,
     `185.199.110.153`, `185.199.111.153`
   - Subdomain (`www.example.com`): one `CNAME` → `<username>.github.io`
3. **Settings → Pages → Custom domain**: enter the domain, save (this creates a `CNAME`
   file in the repo automatically), then enable **Enforce HTTPS** once the certificate
   finishes provisioning — usually a few minutes, occasionally up to an hour.

Then add the canonical URL to `<head>` in `index.html`:

```html
<meta property="og:url" content="https://yourdomain.com/">
```

## Search visibility

`index.html` currently carries `<meta name="robots" content="noindex, nofollow">`, which keeps
the page out of search results while the URL still works for anyone it is shared with.

**Delete that tag when you want to be discoverable** — typically once the custom domain is
attached and the content is final. Removing it is the whole change; search engines pick the
page up on their next crawl.

## Keeping it current

- **Latest post card** (`index.html`, in the "What I'm studying" section) — title, date,
  summary, and the two links to the blog.
- **Link-preview card** (`images/og-card.jpg`, 1200×630) — regenerate if the headline
  or headshot changes.
- **Experience and publications** — plain HTML, edit in place.
