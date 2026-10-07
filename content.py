"""Static page content: styles, the comparison grid, notes and sources.

Kept apart from app.py so the logic stays easy to read.
"""

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500..800&family=IBM+Plex+Mono:wght@400;500;600&family=Public+Sans:wght@400;500;600;700&display=swap');
:root {
  --bg: #f3f5f8; --surface: #ffffff; --surface-2: #eceff5; --fg: #141c2b; --muted: #566176;
  --line: #d8dde7; --accent: #2c4ea6; --accent-soft: #e2e8f8; --loss: #b4441a; --loss-soft: #f6e3d9;
  --win: #18744e; --win-soft: #d9efe3; --warn: #8a5a00; --warn-soft: #fbf0d9;
  --font-display: "Bricolage Grotesque", "Avenir Next", "Segoe UI", system-ui, sans-serif;
  --font-body: "Public Sans", "Segoe UI", system-ui, -apple-system, sans-serif;
  --font-data: "IBM Plex Mono", ui-monospace, Menlo, Consolas, monospace;
}
[data-testid="stMainBlockContainer"], .block-container { max-width: 880px; padding-top: 4rem; }
html, body, [data-testid="stAppViewContainer"] { font-family: var(--font-body); }
h1, h2, h3 { font-family: var(--font-display) !important; letter-spacing: -0.015em; }
.pg-eyebrow { font: 600 12px/1.2 var(--font-body); letter-spacing: .08em; text-transform: uppercase; color: var(--muted); margin: 0; }
.pg-h1 { font-family: var(--font-display); font-weight: 760; font-size: clamp(34px, 6vw, 50px); line-height: 1.02; letter-spacing: -0.025em; margin: 8px 0 12px; color: var(--fg); }
.pg-lede { color: var(--muted); font-size: 16px; max-width: 62ch; margin: 0 0 10px; }
.pg-hours { display: grid; grid-template-columns: repeat(24, 1fr); gap: 2px; height: 14px; max-width: 520px; margin-top: 14px; }
.pg-hours span { background: var(--surface-2); border-radius: 2px; }
.pg-hours span.eve { background: var(--loss); }
.pg-hours-note { font-size: 13.5px; color: var(--muted); margin: 6px 0 0; }
.pg-hours-note b { color: var(--loss); }

.pg-card { background: var(--surface); border: 1px solid var(--line); border-radius: 10px; padding: 20px 22px; box-shadow: 0 1px 2px rgb(20 28 43 / .08); margin-bottom: 12px; }
.pg-k { font-size: 13.5px; color: var(--muted); margin: 0; }
.pg-big { font-family: var(--font-display); font-weight: 760; font-size: clamp(42px, 8vw, 60px); line-height: 1; letter-spacing: -0.025em; color: var(--loss); margin: 8px 0 8px; font-variant-numeric: tabular-nums; }
.pg-big small { font-size: 18px; font-weight: 600; color: var(--muted); letter-spacing: 0; margin-left: 4px; }
.pg-sub { font-size: 14px; color: var(--muted); margin: 0; }
.pg-sub b { color: var(--fg); }
.pg-range { margin-top: 14px; padding: 10px 12px; background: var(--surface-2); border-radius: 8px; font-size: 14px; }
.pg-range b { font-family: var(--font-data); }
.pg-bar { display: flex; height: 14px; border-radius: 7px; overflow: hidden; background: var(--loss); margin: 4px 0 12px; }
.pg-bar .rec { background: var(--win); }
.pg-split { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.pg-v { font: 700 24px/1.1 var(--font-display); font-variant-numeric: tabular-nums; margin: 2px 0 0; }
.pg-v.win { color: var(--win); } .pg-v.loss { color: var(--loss); }
.pg-note { font-size: 13.5px; color: var(--muted); margin: 10px 0 0; }
.pg-stats { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; margin-top: 4px; }
.pg-stat .n { font: 600 20px/1.1 var(--font-data); margin: 0 0 4px; color: var(--fg); }
.pg-stat .k { font-size: 12.5px; color: var(--muted); line-height: 1.3; margin: 0; }

.pg-agency h3 { font-size: 24px; margin: 2px 0 4px; color: var(--fg); }
.pg-agency .match { font-size: 13.5px; color: var(--muted); margin: 0 0 12px; }
.pg-facts { display: grid; grid-template-columns: 150px minmax(0, 1fr); gap: 8px 14px; font-size: 14px; margin: 0; }
.pg-facts dt { color: var(--muted); }
.pg-facts dd { margin: 0; color: var(--fg); min-width: 0; overflow-wrap: anywhere; }
@media (max-width: 560px) { .pg-facts { grid-template-columns: 1fr; gap: 2px; } .pg-facts dd { margin-bottom: 8px; } }
.pg-flag { border-radius: 8px; padding: 10px 12px; font-size: 14px; margin-top: 10px; }
.pg-flag.warn { background: var(--warn-soft); color: var(--warn); }
.pg-flag.info { background: var(--accent-soft); color: var(--accent); }
.pg-flag.note { background: var(--surface-2); color: var(--muted); }
.pg-quote { border-left: 3px solid var(--loss); padding: 4px 0 4px 12px; margin: 8px 0; font-size: 14px; }
.pg-quote span { display: block; color: var(--muted); font-size: 12.5px; margin-top: 2px; }

.tag { display: inline-block; font: 600 10.5px/1 var(--font-body); letter-spacing: .05em; text-transform: uppercase; padding: 4px 6px; border-radius: 4px; margin-right: 6px; vertical-align: 1px; }
.tag-data { background: var(--accent-soft); color: var(--accent); }
.tag-assume { background: var(--surface-2); color: var(--muted); box-shadow: inset 0 0 0 1px var(--line); }
.tag-found { background: var(--win-soft); color: var(--win); }
.tag-claim { background: var(--win-soft); color: var(--win); }
.pg-src { font-size: 13px; color: var(--muted); margin: -4px 0 14px; line-height: 1.45; }
.pg-src a, .pg-card a, .pg-sources a, .pg-notes a { color: var(--accent); }
.pg-group { font: 600 12px/1.2 var(--font-body); letter-spacing: .08em; text-transform: uppercase; color: var(--muted); margin: 18px 0 8px; border-top: 1px solid var(--line); padding-top: 14px; }

.pg-scroll { overflow-x: auto; border: 1px solid var(--line); border-radius: 10px; background: var(--surface); margin-bottom: 8px; }
.pg-scroll table { border-collapse: collapse; width: 100%; margin: 0; border: 0; }
.pg-scroll th { text-align: left; font: 600 11.5px/1.3 var(--font-body); letter-spacing: .06em; text-transform: uppercase; color: var(--muted); padding: 10px 12px; border: 0; border-bottom: 1px solid var(--line); background: var(--surface-2); vertical-align: bottom; }
.pg-scroll td { padding: 10px 12px; border: 0; border-bottom: 1px solid var(--line); vertical-align: top; font-size: 14px; color: var(--fg); }
.pg-scroll tr:last-child td, .pg-scroll tr:last-child th { border-bottom: 0; }
.sheet { min-width: 620px; }
.sheet .ref { font: 600 13px var(--font-data); color: var(--muted); width: 2.4em; }
.sheet td.w { font: 400 13px/1.45 var(--font-data); color: var(--muted); }
.sheet .r { text-align: right; white-space: nowrap; }
.sheet td.r { font: 500 14px var(--font-data); font-variant-numeric: tabular-nums; }
.sheet tr.money td { font-weight: 700; } .sheet tr.money td.r { color: var(--loss); }
.sheet tr.recov td.r { color: var(--win); font-weight: 600; }
.sheet tr.soft td { background: var(--surface-2); }
.pg-foot { font-size: 13px; color: var(--muted); margin: 6px 0 0; }

.fit { min-width: 760px; }
.fit tbody th { font: 600 14px/1.35 var(--font-body); letter-spacing: 0; text-transform: none; color: var(--fg); background: var(--surface); width: 160px; position: sticky; left: 0; z-index: 1; vertical-align: top; }
.fit thead th:first-child { position: sticky; left: 0; z-index: 1; }
.fit th small { display: block; font: 400 12px/1.3 var(--font-body); letter-spacing: 0; text-transform: none; margin-top: 3px; }
.fit td.us, .fit th.us { background: var(--accent-soft); }
.fit th.us { color: var(--fg); }
.st { display: inline-block; font: 600 12px/1 var(--font-body); padding: 4px 8px; border-radius: 999px; margin-bottom: 5px; white-space: nowrap; }
.st-yes { background: var(--win-soft); color: var(--win); }
.st-part { background: var(--surface); color: var(--accent); box-shadow: inset 0 0 0 1px var(--accent); }
.st-ns { color: var(--muted); box-shadow: inset 0 0 0 1px var(--line); }
.st-no { background: var(--surface-2); color: var(--muted); }
.fit .d { display: block; color: var(--muted); font-size: 12.5px; line-height: 1.4; }
.ref { font: 600 10px var(--font-data); text-decoration: none; }

.pg-answer blockquote { margin: 6px 0 0; padding: 0; border: 0; font-family: var(--font-display); font-size: clamp(19px, 2.6vw, 23px); font-weight: 600; line-height: 1.3; color: var(--fg); }
.pg-answer blockquote em { font-style: normal; color: var(--win); }
.pg-notes { padding-left: 18px; font-size: 14.5px; color: var(--fg); }
.pg-notes li { margin-bottom: 6px; }
.pg-sources { padding-left: 22px; font-size: 14px; }
.pg-sources li { margin-bottom: 4px; }
.pg-sources span { color: var(--muted); }
.pg-footer { border-top: 1px solid var(--line); margin-top: 28px; padding-top: 14px; font-size: 13px; color: var(--muted); }
"""

HEADER = """
<p class="pg-eyebrow">A prototype by Zak for Nesti</p>
<div class="pg-h1">Phone Gap Calculator</div>
<p class="pg-lede">Type in any UK estate or letting agency. The calculator researches it online and estimates the fee income it loses each year to phone calls nobody answers out of hours, and how much comes back when AI answers the phone as well as the messages.</p>
<div class="pg-hours" aria-hidden="true">""" + "".join(
    f'<span class="{"eve" if 18 <= h < 21 else ""}"></span>' for h in range(24)
) + """</div>
<p class="pg-hours-note">InStep AI rang 3,047 UK agency numbers between 6pm and 9pm on weekdays. <b>94% went unanswered.</b><sup><a class="ref" href="#s1">1</a></sup></p>
"""

FIT = """
<div class="pg-scroll"><table class="fit">
<thead><tr>
  <th>Can it…</th>
  <th class="us">Nesti<small>AI workforce</small></th>
  <th>Alto Lead Flow<small>CRM AI, powered by BridgeAI</small></th>
  <th>EstateAgents.ai<small>Outbound AI voice</small></th>
  <th>Answerphone<small>Voicemail box</small></th>
</tr></thead>
<tbody>
<tr><th>Answer phone calls</th>
  <td class="us"><span class="st st-yes">Yes</span><span class="d">Every call picked up in under a second, 24/7.<sup><a class="ref" href="#s8">8</a></sup></span></td>
  <td><span class="st st-ns">Not listed</span><span class="d">Alto lists portals, email, WhatsApp and web.<sup><a class="ref" href="#s4">4</a></sup></span></td>
  <td><span class="st st-ns">Not stated</span><span class="d">Reported as outbound calling.<sup><a class="ref" href="#s11">11</a></sup></span></td>
  <td><span class="st st-part">Takes a message</span></td></tr>
<tr><th>Handle WhatsApp and portal enquiries</th>
  <td class="us"><span class="st st-yes">Yes</span><span class="d">Calls, WhatsApp, SMS, email, portal enquiries and web chat.<sup><a class="ref" href="#s8">8</a></sup></span></td>
  <td><span class="st st-yes">Yes</span><span class="d">"Every enquiry from portals, email, WhatsApp or web is answered instantly."<sup><a class="ref" href="#s4">4</a></sup></span></td>
  <td><span class="st st-ns">Not stated</span></td>
  <td><span class="st st-no">No</span></td></tr>
<tr><th>Book viewings and valuations</th>
  <td class="us"><span class="st st-yes">Yes, both</span><span class="d">Into the right negotiator's diary, allowing for travel time.<sup><a class="ref" href="#s9">9</a></sup></span></td>
  <td><span class="st st-part">Viewings</span><span class="d">Books viewings into the Alto diary. Valuations not stated.<sup><a class="ref" href="#s4">4</a></sup></span></td>
  <td><span class="st st-part">Passes leads on</span><span class="d">Qualified contacts go to branch teams as valuation leads.<sup><a class="ref" href="#s11">11</a></sup></span></td>
  <td><span class="st st-no">No</span></td></tr>
<tr><th>Call old leads</th>
  <td class="us"><span class="st st-yes">Yes</span><span class="d">Makes outbound calls and brings back valuations that never converted.<sup><a class="ref" href="#s9">9</a></sup></span></td>
  <td><span class="st st-ns">Not stated</span></td>
  <td><span class="st st-yes">Yes</span><span class="d">Calls former applicants, historic enquiries and dormant contacts.<sup><a class="ref" href="#s11">11</a></sup></span></td>
  <td><span class="st st-no">No</span></td></tr>
<tr><th>Handle tenants and maintenance</th>
  <td class="us"><span class="st st-yes">Yes</span><span class="d">Answers tenants and landlords, logs maintenance, instructs contractors.<sup><a class="ref" href="#s7">7</a></sup></span></td>
  <td><span class="st st-ns">Not stated</span></td>
  <td><span class="st st-ns">Not stated</span></td>
  <td><span class="st st-no">No</span></td></tr>
<tr><th>Work across several CRMs</th>
  <td class="us"><span class="st st-yes">Yes</span><span class="d">Alto, Reapit, Street, Rex, SME Professional, Acquaint and more.<sup><a class="ref" href="#s10">10</a></sup></span></td>
  <td><span class="st st-part">Alto</span><span class="d">Alto's own product, writing to the Alto diary.<sup><a class="ref" href="#s4">4</a></sup></span></td>
  <td><span class="st st-ns">Not stated</span></td>
  <td><span class="st st-no">No</span></td></tr>
</tbody></table></div>
<p class="pg-foot">Filled only from public pages; "Not stated" means the page doesn't say. Some CRMs now answer calls themselves: Street lists an AI Call Handler that answers inbound calls 24/7.<sup><a class="ref" href="#s12">12</a></sup> This grid uses Alto Lead Flow as the CRM example. Nesti is listed in Alto's own integration marketplace.<sup><a class="ref" href="#s6">6</a></sup></p>
"""

ANSWER = """
<div class="pg-card pg-answer">
  <p class="pg-eyebrow">When an agent says "my CRM already does AI"</p>
  <blockquote>Great, keep it for text.<br><em>Nesti answers the phone</em>, works your old leads and handles tenants,<br>and logs everything back into your CRM.</blockquote>
</div>
"""

NOTES = """
<ul class="pg-notes">
  <li>The 94% and 27% figures come from InStep AI, which sells voice AI. Its mystery calls covered weekday evenings, 6pm to 9pm. This calculator applies that rate to all out-of-hours calls, weekends included.<sup><a class="ref" href="#s1">1</a></sup></li>
  <li>27% is the share of leads on all channels that arrived out of hours for InStep's clients. It is used here as the share of calls. Other suppliers publish figures from 26% to 65%, and none is independent.<sup><a class="ref" href="#s2">2</a></sup></li>
  <li>Calls per month, valuation share, competitor rate and conversion rate are assumptions. Swap in the agency's own figures.</li>
  <li>For a looked-up agency, the fee comes from local prices: 1.2% of the average house price for sales (the low end of typical sole-agency fees, 1.2% to 1.8% inc VAT)<sup><a class="ref" href="#s13">13</a></sup> and 12% of a year's rent for lettings (10% + VAT, the low end of fully managed fees)<sup><a class="ref" href="#s14">14</a></sup>. Agencies doing both get the average of the two.</li>
  <li>Agency details come from an AI web search of public pages. Check the linked sources before quoting them to anyone.</li>
  <li>Recovery with Nesti uses Nesti's own claim that 95%+ of enquiries are handled start to finish.<sup><a class="ref" href="#s7">7</a></sup></li>
  <li>Sanity check: Alto's own Lead Flow calculator estimates £40,000–£50,000+ a year recovered for a typical single-branch agency, using different assumptions.<sup><a class="ref" href="#s5">5</a></sup></li>
</ul>
"""

SOURCES = """
<ol class="pg-sources">
  <li id="s1"><a href="https://propertyindustryeye.com/agents-miss-94-of-evening-calls-study-finds/" target="_blank">Agents miss 94% of evening calls, study finds</a> <span>Property Industry Eye, 5 Aug 2026 (InStep AI study)</span></li>
  <li id="s2"><a href="https://thenegotiator.co.uk/news/products-services-news/how-many-property-enquiries-really-arrive-after-hours/" target="_blank">How many property enquiries really arrive after hours?</a> <span>The Negotiator, 27 Jul 2026</span></li>
  <li id="s3"><a href="https://www.altosoftware.co.uk/lead-flow/" target="_blank">Alto Lead Flow</a> <span>Alto product page</span></li>
  <li id="s4"><a href="https://support.altosoftware.co.uk/hc/en-gb/articles/5048172508575-Alto-Lead-Flow-powered-by-Bridge-AI" target="_blank">Alto Lead Flow (powered by Bridge AI)</a> <span>Alto Help Centre</span></li>
  <li id="s5"><a href="https://www.altosoftware.co.uk/wp-content/themes/alto/embed/lead-flow.html" target="_blank">Alto Lead Flow calculator</a> <span>Alto</span></li>
  <li id="s6"><a href="https://www.altosoftware.co.uk/integrations/nesti/" target="_blank">Nesti integration</a> <span>Alto integrations marketplace</span></li>
  <li id="s7"><a href="https://www.nesti.io/" target="_blank">Nesti homepage</a> <span>nesti.io</span></li>
  <li id="s8"><a href="https://www.nesti.io/workforce/ai-receptionist" target="_blank">AI Receptionist</a> <span>nesti.io</span></li>
  <li id="s9"><a href="https://www.nesti.io/workforce/ai-negotiator" target="_blank">AI Negotiator</a> <span>nesti.io</span></li>
  <li id="s10"><a href="https://www.nesti.io/integrations" target="_blank">Integrations</a> <span>nesti.io</span></li>
  <li id="s11"><a href="https://propertyindustryeye.com/estate-agency-leads-to-be-contacted-by-ai-voice-system/" target="_blank">Estate agency leads to be contacted by AI voice system</a> <span>Property Industry Eye, 7 May 2026 (EstateAgents.ai)</span></li>
  <li id="s12"><a href="https://street.co.uk/product/index/ai-call-handler" target="_blank">AI Call Handler</a> <span>Street</span></li>
  <li id="s13"><a href="https://hoa.org.uk/advice/guides-for-homeowners/i-am-selling/how-do-i-lower-my-estate-agent-fees-use-online-agents/" target="_blank">Estate agent fees and how you can save in 2026</a> <span>HomeOwners Alliance</span></li>
  <li id="s14"><a href="https://www.landlordvision.co.uk/blog/buy-to-let-management-costs/" target="_blank">Buy-to-let management costs</a> <span>LandlordVision, May 2026</span></li>
</ol>
"""

FOOTER = """
<div class="pg-footer">Phone Gap Calculator · a prototype by Zak · October 2026<br>
Not affiliated with or endorsed by Nesti, Alto or any agency or company named. Figures are estimates for discussion.</div>
"""
