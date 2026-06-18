<?xml version="1.0" encoding="UTF-8"?>
<!--
  Browser-only stylesheet for rss.xml. When someone opens the feed in a browser,
  this renders a friendly page instead of raw XML. RSS reader apps ignore it and
  parse the underlying feed directly, so subscriptions still work.
-->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="html" encoding="UTF-8" indent="yes"/>
  <xsl:template match="/rss/channel">
    <html lang="en">
      <head>
        <meta charset="UTF-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
        <title><xsl:value-of select="title"/> — RSS feed</title>
        <style>
          :root { --bg:#0b0d17; --panel:#141728; --text:#e7e9f3; --muted:#9aa0bd; --accent:#7c5cff; --accent2:#22d3ee; --border:rgba(255,255,255,.08); }
          * { box-sizing:border-box; }
          body { margin:0; background:var(--bg); color:var(--text); font-family:"Inter",system-ui,-apple-system,Segoe UI,Roboto,sans-serif; line-height:1.55; }
          .wrap { max-width:780px; margin:0 auto; padding:40px 20px 60px; }
          h1 { font-size:2rem; font-weight:800; margin:0 0 6px;
               background:linear-gradient(100deg,#fff,var(--accent2),var(--accent),#fff); background-size:200% auto;
               -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; }
          .note { background:var(--panel); border:1px solid var(--border); border-radius:12px; padding:14px 16px; margin:14px 0 26px; color:var(--muted); font-size:.92rem; }
          .note b { color:var(--text); }
          .url { display:block; margin-top:8px; padding:9px 12px; background:#0b0d17; border:1px solid var(--border); border-radius:8px; color:var(--accent2); font-family:ui-monospace,Menlo,monospace; font-size:.85rem; word-break:break-all; }
          a { color:var(--accent2); text-decoration:none; }
          a:hover { text-decoration:underline; }
          .item { padding:14px 0; border-bottom:1px solid var(--border); }
          .meta { font-size:.78rem; color:var(--muted); margin-bottom:4px; }
          .cat { display:inline-block; padding:2px 8px; border-radius:999px; border:1px solid var(--border); color:var(--text); margin-right:6px; }
          .item .title { font-size:1.02rem; font-weight:700; color:var(--text); }
          .desc { margin:6px 0 0; color:var(--text); opacity:.88; font-size:.92rem; }
        </style>
      </head>
      <body>
        <div class="wrap">
          <h1>📡 <xsl:value-of select="title"/></h1>
          <div class="note">
            <b>This is an RSS feed</b> — a list of updates for apps, not a normal web page.
            To follow the radar, paste this address into any RSS reader (Feedly, Inoreader, NetNewsWire…):
            <span class="url"><xsl:value-of select="link"/>rss.xml</span>
          </div>
          <p><a href="{link}">← Back to the website</a></p>
          <xsl:for-each select="item">
            <div class="item">
              <div class="meta">
                <span class="cat"><xsl:value-of select="category"/></span>
                <xsl:value-of select="pubDate"/>
              </div>
              <a class="title" href="{link}"><xsl:value-of select="title"/></a>
              <p class="desc"><xsl:value-of select="description"/></p>
            </div>
          </xsl:for-each>
        </div>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
