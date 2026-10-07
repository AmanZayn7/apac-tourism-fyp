"""Local destination artwork and presentation metadata. No remote assets or tracking."""

import base64
from html import escape

DESTINATIONS = {
    "Bangkok": {
        "eyebrow": "THAILAND PROXY",
        "headline": "Bangkok",
        "tagline": "Golden silhouettes. A city in motion.",
        "accent": "#CB6247",
        "soft": "#F4E4D2",
        "code": "BKK",
        "sky": "#EDBB7E",
    },
    "Singapore": {
        "eyebrow": "SINGAPORE",
        "headline": "Singapore",
        "tagline": "Garden greens. A changing horizon.",
        "accent": "#168B80",
        "soft": "#DAEBDF",
        "code": "SIN",
        "sky": "#A4D8C2",
    },
    "Hong Kong": {
        "eyebrow": "HONG KONG",
        "headline": "Hong Kong",
        "tagline": "Harbour lights. A thousand perspectives.",
        "accent": "#6266AD",
        "soft": "#EEDCE4",
        "code": "HKG",
        "sky": "#D8B4BE",
    },
}


def skyline_svg(city):
    """Original stylized illustrations, decorative rather than geographic maps."""
    sky = DESTINATIONS[city]["sky"]
    if city == "Bangkok":
        shapes = """<g fill="#EBD3A3"><path d="M280 260V207H300V184H319V155H328V104L337 155H346V184H365V207H385V260Z"/><path d="M422 267V233H440V213H455V182H461V135L468 182H477V213H491V233H509V267Z"/></g>
        <g fill="#183F3B"><path d="M200 299V269H222L260 231L298 269H321V299Z"/><path d="M355 308V270H377L407 219L437 270H458V308Z"/><path d="M521 312V255H539V229H550V183L560 229H573V255H590V312Z"/></g>
        <g fill="#F8EACC"><rect x="243" y="271" width="12" height="28"/><rect x="270" y="271" width="12" height="28"/><rect x="399" y="276" width="13" height="32"/></g>"""
    elif city == "Singapore":
        shapes = """<g fill="#D7E9CD"><path d="M245 270L258 129H291L301 270Z"/><path d="M315 270L328 129H361L371 270Z"/><path d="M385 270L398 129H431L441 270Z"/><path d="M232 123Q334 98 453 120L442 139Q335 153 245 138Z"/></g>
        <g stroke="#89BBA5" stroke-width="4"><path d="M270 147L259 250M338 148L327 252M408 148L397 252"/></g>
        <g stroke="#C8DBA6" stroke-width="6" fill="none"><path d="M502 279V210M559 285V191M605 282V228"/></g><g fill="#779E71"><path d="M470 206Q502 225 534 206L524 198Q501 206 480 198Z"/><path d="M523 187Q559 208 595 187L583 177Q559 189 535 177Z"/><path d="M581 224Q605 240 629 224L620 216Q604 224 590 216Z"/></g>"""
    else:
        shapes = """<path d="M90 272L210 195L251 218L342 169L444 225L536 186L655 270Z" fill="#639489" opacity=".55"/>
        <g fill="#D9D7CF"><path d="M270 290V180L298 151L326 180V290Z"/><path d="M389 292V152H398V93H419V152H428V292Z"/><path d="M474 292V189H514V292Z"/><path d="M547 292V221H584V292Z"/></g>
        <g stroke="#5B8279" fill="none" stroke-width="3"><path d="M274 184L322 234L274 278M321 184L274 234L321 278M405 160V278M491 198V279"/></g>
        <path d="M306 326H383L368 338H324Z" fill="#F3D69D"/><path d="M340 320V277L360 317Z" fill="#D78F72"/><path d="M335 320V291L317 316Z" fill="#C67565"/>"""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 680 380" role="img" aria-label="Stylized {escape(city)} skyline"><defs><linearGradient id="sky" x2="0" y2="1"><stop stop-color="{sky}" stop-opacity=".32"/><stop offset="1" stop-color="#153F3B" stop-opacity="0"/></linearGradient></defs><rect width="680" height="380" fill="url(#sky)"/><path d="M156 100Q178 79 196 98Q216 58 249 93Q272 78 289 105" fill="none" stroke="#FFF1CC" stroke-width="2" opacity=".6"/><path d="M460 42Q477 21 495 39Q523 15 547 42" fill="none" stroke="#FFF1CC" stroke-width="2" opacity=".45"/><circle cx="438" cy="103" r="63" fill="{sky}" opacity=".78"/><path d="M190 98Q277 42 348 65" stroke="#F4EAD5" stroke-opacity=".55" fill="none" stroke-dasharray="3 7"/><path d="M345 58L365 64L347 72L351 64Z" fill="#F4EAD5"/>{shapes}<path d="M160 310Q285 296 460 308T680 306V380H160Z" fill="#A7C5B2" opacity=".15"/><g stroke="#DFEAD5" opacity=".25"><path d="M232 343H306M407 334H475M489 353H615M336 362H414"/></g></svg>'''


def hero(city, observed_end, model_count):
    item = DESTINATIONS[city]
    art = base64.b64encode(skyline_svg(city).encode()).decode()
    return f'''<section class="destination-hero" aria-label="{escape(city)} destination overview"><img class="hero-art" src="data:image/svg+xml;base64,{art}" alt="Illustrated {escape(city)} skyline"/><div class="hero-copy"><span class="hero-kicker">A WINDOW INTO THE YEAR AHEAD</span><h1>{item["headline"]}<span class="hero-dot">.</span></h1><p>{item["tagline"]}</p><span class="hero-stamp">{item["code"]} &nbsp; / &nbsp; TWELVE-MONTH ARRIVAL FORECAST</span></div><div class="hero-bottom"><span>03 destinations · {model_count:02d} forecast models</span><span>Observations through {observed_end}</span></div></section>'''
