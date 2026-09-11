"""
Build DepScan landing page by directly transforming the scraped WriteMate HTML.
Maintains 100% of WriteMate layout, Tailwind classes, and styling while updating
the branding, headlines, hero CTA, ecosystem bar, and supply chain security text.
"""

import re

def main():
    with open("frontend/scraped_writemate.html", "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Update title and link CSS
    html = html.replace(
        "WriteMate AI - Content Creation at Its Best",
        "DepScan — Software Supply Chain Security & AI Auto-Remediation"
    )
    html = html.replace('href="/assets/index-CdLNTYUv.css"', 'href="/static/writemate.css"')
    html = html.replace('src="/assets/index-DA8RDcsB.js"', 'src="/static/landing.js"')

    # 2. Update Logo and brand in header
    old_logo = '<a href="/" data-discover="true"><img alt="WriteMate AI Logo" src="/images/logo.svg"></a>'
    new_logo = '''<a href="/" class="flex items-center gap-3">
        <img alt="DepScan Logo" src="/images/logo.svg" class="h-8 w-auto">
        <span class="text-white font-mono font-bold text-xl tracking-tight">DepScan</span>
        <span class="font-mono text-[10px] px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-400 border border-blue-500/30 font-semibold tracking-wider">SECURITY AI</span>
    </a>'''
    if old_logo in html:
        html = html.replace(old_logo, new_logo, 1)

    # 3. Update Nav Links
    old_nav = '<li><a class="transition-colors duration-300 text-white" href="/" data-discover="true">Home</a></li><li><a class="transition-colors duration-300 text-white/60" href="/pricing" data-discover="true">Pricing</a></li><li><a class="transition-colors duration-300 text-white/60" href="/docs" data-discover="true">Docs</a></li><li><a class="transition-colors duration-300 text-white/60" href="/support" data-discover="true">Support</a></li>'
    new_nav = '<li><a class="transition-colors duration-300 text-white" href="#capabilities">Capabilities</a></li><li><a class="transition-colors duration-300 text-white/60 hover:text-white" href="#ecosystems">Ecosystems</a></li><li><a class="transition-colors duration-300 text-white/60 hover:text-white" href="#use-cases">Use Cases</a></li><li><a class="transition-colors duration-300 text-white/60 hover:text-white" href="#faq">FAQ</a></li><li><a class="transition-colors duration-300 text-white/60 hover:text-white" href="/docs" target="_blank">API Docs</a></li>'
    if old_nav in html:
        html = html.replace(old_nav, new_nav, 1)

    # 4. Header buttons: link Start for free and Login directly to /dashboard
    html = html.replace(
        'href="/pricing" data-discover="true"><span class="block relative h-full w-full overflow-hidden"><span class="flex h-full w-full items-center justify-center" style="transform: none;">Start for free</span>',
        'href="/dashboard"><span class="block relative h-full w-full overflow-hidden"><span class="flex h-full w-full items-center justify-center" style="transform: none;">Start for free</span>'
    )
    html = html.replace(
        'href="/pricing" data-discover="true"><span class="block relative h-full w-full overflow-hidden"><span class="flex h-full w-full items-center justify-center" style="transform: none;">Login</span>',
        'href="/dashboard"><span class="block relative h-full w-full overflow-hidden"><span class="flex h-full w-full items-center justify-center" style="transform: none;">Dashboard</span>'
    )

    # 5. Main Hero Headline & Subheadline
    old_h1 = '<h1 class="text-4xl lg:text-5xl -tracking-[1.5px] xl:text-6xl font-normal text-white text-center xl:leading-16 mb-6" style="opacity: 1; transform: none;">Write Better. Reply Faster. Understand Anything with AI.</h1>'
    new_h1 = '<h1 class="text-4xl lg:text-5xl -tracking-[1.5px] xl:text-6xl font-normal text-white text-center xl:leading-16 mb-6" style="opacity: 1; transform: none;">Scan Smarter. Patch Faster.<br><span class="text-transparent bg-clip-text bg-gradient-to-r from-white via-blue-200 to-blue-400">Secure Every Dependency.</span></h1>'
    if old_h1 in html:
        html = html.replace(old_h1, new_h1, 1)

    old_sub = '<p class="text-white/80 text-base max-w-lg text-center mx-auto mb-8 xl:mb-14" style="opacity: 1; transform: none;">Your all-in-one AI writing platform — generate copy, summarize PDFs, write emails, and transform tone instantly.</p>'
    new_sub = '<p class="text-white/80 text-base max-w-xl text-center mx-auto mb-8 xl:mb-14" style="opacity: 1; transform: none;">Your all-in-one software supply chain security analyzer — identify risky dependencies, typosquatting indicators, build provenance flaws, and synthesize 1-click AI remediation patches.</p>'
    if old_sub in html:
        html = html.replace(old_sub, new_sub, 1)

    # 6. Hero Input: Replace "Write a linkedin post about a new AI tool..." with interactive repo input + Start for free
    old_input_box = '<div class="relative max-w-[500px] mx-auto" style="opacity: 1; transform: none;"><input class="text-sm text-white placeholder:text-white/60 p-8 pl-6 pr-20 bg-theme-dark-500 h-16 w-full focus:outline-0" placeholder="Write a linkedin post about a new AI tool..." type="text"><div class="absolute right-2 size-12 top-1/2 -translate-y-1/2 z-10"><button class="cursor-pointer relative overflow-hidden group inline-flex items-center justify-center bg-white size-12 inline-flex items-center justify-center hover:bg-gray-100 transition duration-300"><span class="block relative h-full w-full overflow-hidden"><span class="flex h-full w-full items-center justify-center" style="transform: none;"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M11.9961 3.99902L11.9961 20.0004M6 9.99502L11.9998 3.99902L18 9.99502" stroke="#060606" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"></path></svg></span><span class="absolute top-0 left-0 w-full h-full flex items-center justify-center" style="transform: translateY(100%);"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M11.9961 3.99902L11.9961 20.0004M6 9.99502L11.9998 3.99902L18 9.99502" stroke="#060606" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"></path></svg></span></span></button></div></div>'

    new_input_box = '''<div class="relative max-w-[580px] mx-auto" style="opacity: 1; transform: none;">
    <form onsubmit="handleHeroSubmit(event)" class="relative">
        <input id="hero-repo-url" class="text-sm text-white placeholder:text-white/50 p-8 pl-6 pr-44 bg-theme-dark-500 h-16 w-full focus:outline-none border border-white/20 focus:border-white/50 transition duration-300 font-mono" placeholder="Enter GitHub repo URL (e.g. user/repo)..." type="text" value="https://github.com/Amey2007-FullStack/Test_repo_kurukshetra.git" required>
        <div class="absolute right-2 top-1/2 -translate-y-1/2 z-10">
            <button type="submit" class="cursor-pointer relative overflow-hidden group inline-flex items-center justify-center bg-white text-black font-mono text-sm font-semibold px-5 py-3 hover:bg-gray-100 transition duration-300 gap-1.5 shadow-lg">
                <span>Start for free</span>
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M11.9961 3.99902L11.9961 20.0004M6 9.99502L11.9998 3.99902L18 9.99502" stroke="#060606" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>
            </button>
        </div>
    </form>
    <div class="flex items-center justify-center gap-2 mt-4 text-xs font-mono text-white/60 flex-wrap">
        <span class="text-white/40 uppercase text-[10px]">Sample repos:</span>
        <button type="button" onclick="fillAndSubmit('https://github.com/Amey2007-FullStack/Test_repo_kurukshetra.git')" class="px-2.5 py-1 bg-white/5 hover:bg-white/10 text-white/80 rounded border border-white/10 hover:border-white/30 transition cursor-pointer">⚡ Test_repo_kurukshetra</button>
        <button type="button" onclick="fillAndSubmit('https://github.com/expressjs/express.git')" class="px-2.5 py-1 bg-white/5 hover:bg-white/10 text-white/80 rounded border border-white/10 hover:border-white/30 transition cursor-pointer">📦 expressjs/express</button>
    </div>
</div>'''

    if old_input_box in html:
        html = html.replace(old_input_box, new_input_box, 1)

    # 7. Replace "Trusted by" with "Supported Ecosystems & Registries"
    old_trusted = '<span class="text-white font-mono">Trusted by</span>'
    new_trusted = '<span class="text-white font-mono uppercase tracking-wider text-sm">Supported Ecosystems &amp; Registries</span>'
    if old_trusted in html:
        html = html.replace(old_trusted, new_trusted, 1)

    ecosystems_bar = '''<div id="ecosystems" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 max-w-5xl mx-auto px-4">
    <div class="flex flex-col items-center justify-center p-4 border border-white/10 bg-white/5 hover:border-white/30 transition rounded-lg">
        <span class="text-2xl mb-1">📦</span>
        <span class="text-white font-mono font-bold text-sm">npm</span>
        <span class="text-white/50 text-xs">JavaScript/TS</span>
    </div>
    <div class="flex flex-col items-center justify-center p-4 border border-white/10 bg-white/5 hover:border-white/30 transition rounded-lg">
        <span class="text-2xl mb-1">🐍</span>
        <span class="text-white font-mono font-bold text-sm">PyPI</span>
        <span class="text-white/50 text-xs">Python</span>
    </div>
    <div class="flex flex-col items-center justify-center p-4 border border-white/10 bg-white/5 hover:border-white/30 transition rounded-lg">
        <span class="text-2xl mb-1">🔷</span>
        <span class="text-white font-mono font-bold text-sm">Go</span>
        <span class="text-white/50 text-xs">go.mod / sum</span>
    </div>
    <div class="flex flex-col items-center justify-center p-4 border border-white/10 bg-white/5 hover:border-white/30 transition rounded-lg">
        <span class="text-2xl mb-1">☕</span>
        <span class="text-white font-mono font-bold text-sm">Maven</span>
        <span class="text-white/50 text-xs">Java / pom.xml</span>
    </div>
    <div class="flex flex-col items-center justify-center p-4 border border-white/10 bg-white/5 hover:border-white/30 transition rounded-lg">
        <span class="text-2xl mb-1">🦀</span>
        <span class="text-white font-mono font-bold text-sm">Cargo</span>
        <span class="text-white/50 text-xs">Rust</span>
    </div>
    <div class="flex flex-col items-center justify-center p-4 border border-white/10 bg-white/5 hover:border-white/30 transition rounded-lg">
        <span class="text-2xl mb-1">🐘</span>
        <span class="text-white font-mono font-bold text-sm">Packagist</span>
        <span class="text-white/50 text-xs">PHP / Composer</span>
    </div>
</div>'''

    html = re.sub(
        r'<div class="w-full inline-flex flex-nowrap overflow-hidden mask-\[linear-gradient.*?</ul>\s*</div>',
        ecosystems_bar,
        html,
        flags=re.DOTALL
    )

    # 8. Update "What You Get" section
    html = html.replace(
        'Describe your idea — the AI creates pages, layout, copy, images and SEO meta. Edit visually, publish or export clean HTML/CSS.',
        'Advanced dependency reasoning, blast radius computation, known CVE correlation, and automated Git diff patch synthesis.'
    )

    html = html.replace('AI Blog Writer', 'Dependency Graph & Blast Radius')
    html = html.replace('Social Post Generator', 'Known CVE & GHSA Correlation')
    html = html.replace('SEO Content Writer', 'Typosquatting & Scope Shield')
    html = html.replace('Email Writer', '1-Click Auto-Remediation Patch')

    html = html.replace(
        'Fully WCAG 2.0 compliant, made with best a11y practices',
        'NetworkX graph reasoning computing transitive reach and blast radius for every package.'
    )
    html = html.replace(
        'href="/tools" data-discover="true"><span class="block relative h-full w-full overflow-hidden"><span class="flex h-full w-full items-center justify-center" style="transform: none;">Try now</span>',
        'href="/dashboard"><span class="block relative h-full w-full overflow-hidden"><span class="flex h-full w-full items-center justify-center" style="transform: none;">Try now</span>'
    )

    # 9. Update "Writemate AI Use Cases"
    html = html.replace('Writemate AI Use Cases', 'DepScan Security Use Cases')
    html = html.replace(
        'Harness AI to effortlessly create stunning content with AI-driven design, copy, images, and SEO optimization. Refine, publish, or export as clean HTML/CSS.',
        'Empower security engineers, DevOps, and developers to eliminate supply chain vulnerabilities before code reaches production.'
    )

    html = html.replace('Innovative product design', 'Monorepo & Polyglot Auditing')
    html = html.replace('Focus on user experience to enhance customer satisfaction.', 'Recursively discover and trace dependencies across npm, PyPI, Go, Maven, and Cargo simultaneously.')

    html = html.replace('Data-driven decision making', 'Pre-Deployment CI/CD Pipeline Gates')
    html = html.replace('Leverage analytics to guide your business strategy.', 'Deterministic risk thresholds (P0-P3) to block compromised dependencies from production builds.')

    html = html.replace('Sustainable business practices', 'Zero-Day Dependency Confusion Shield')
    html = html.replace('Implement eco-friendly initiatives to attract conscious consumers.', 'Levenshtein distance checks preventing public registry substitution and internal scope hijacking.')

    html = html.replace('Effective team collaboration', 'Transitive Blast Radius Impact')
    html = html.replace('Encourage open communication to boost productivity.', 'Compute exact mathematical blast radius across entire upstream and downstream service graphs.')

    html = html.replace('Agile project management', 'Lifecycle Script Execution Audits')
    html = html.replace('Adopt flexibility to adapt to changing market demands.', 'Inspect npm preinstall/postinstall hooks for hidden remote execution or credential exfiltration.')

    html = html.replace('Customer-centric approaches', 'Gemini AI Exploit Reasoning')
    html = html.replace('Prioritize customer feedback to improve service offerings.', 'Synthesize real-world attacker exploit scenarios and produce 1-click unified Git diff patches.')

    # 10. Pricing section: link buttons to /dashboard
    html = html.replace('href="/pricing"', 'href="/dashboard"')

    # 11. Testimonials text
    html = html.replace(
        'Using this AI tool has transformed the way I approach my marketing campaigns. Efficiency has skyrocketed!',
        'DepScan identified a critical prototype pollution in our transitive dependency tree and generated a clean git diff patch in seconds!'
    )
    html = html.replace(
        "The best investment I've made for my business. The AI generates content that truly resonates with my audience.",
        'The dependency reasoning and blast radius analysis gave our security team clear visibility into which CVEs were actually dangerous.'
    )

    # 12. FAQ Section: supply chain questions
    html = html.replace('What is Writemate AI?', 'What is DepScan?')
    html = html.replace('How does the AI writing assistant work?', 'How does DepScan calculate the Blast Radius?')
    html = html.replace('Can I try Writemate AI for free?', 'How does DepScan ensure Zero Code Execution?')
    html = html.replace('What types of content can I create?', 'Which package ecosystems are supported?')
    html = html.replace('Is my data secure?', 'What if Gemini API key is not configured?')

    # Add FAQ answers and click handlers
    html = html.replace(
        '<h3 class="text-lg text-zinc-50 -tracking-[0.18px]">What is DepScan?</h3>',
        '<h3 class="text-lg text-zinc-50 -tracking-[0.18px]">What is DepScan?</h3><p class="faq-ans text-white/70 text-sm mt-3 hidden">DepScan is an automated Software Supply Chain Security Analyzer that identifies risky dependencies, suspicious package behavior, typosquatting, and generates 1-click AI remediation patches.</p>'
    )
    html = html.replace(
        '<h3 class="text-lg text-zinc-50 -tracking-[0.18px]">How does DepScan calculate the Blast Radius?</h3>',
        '<h3 class="text-lg text-zinc-50 -tracking-[0.18px]">How does DepScan calculate the Blast Radius?</h3><p class="faq-ans text-white/70 text-sm mt-3 hidden">DepScan builds directed NetworkX dependency trees. If a child package is compromised, it traces all upstream ancestor services that rely on it to compute an impact blast radius from 0.10 to 1.00.</p>'
    )
    html = html.replace(
        '<h3 class="text-lg text-zinc-50 -tracking-[0.18px]">How does DepScan ensure Zero Code Execution?</h3>',
        '<h3 class="text-lg text-zinc-50 -tracking-[0.18px]">How does DepScan ensure Zero Code Execution?</h3><p class="faq-ans text-white/70 text-sm mt-3 hidden">DepScan uses pure static AST and manifest parsing. No package manager install hooks, setup scripts, or postinstall commands are ever executed, ensuring safe analysis of untrusted repositories.</p>'
    )

    # 13. Bottom CTA Section
    html = html.replace('Ready to write 10× faster?', 'Ready to secure your software supply chain?')
    html = html.replace(
        'Create a professional website in minutes — no coding, no hassle.',
        'Analyze your repositories, discover hidden blast radius threats, and generate 1-click Git patches in seconds.'
    )
    html = html.replace('Explore templates', 'API Documentation')
    html = html.replace('href="/tools"', 'href="/docs"')

    # 14. Footer branding
    html = html.replace('WriteMate', 'DepScan')
    html = html.replace('Writemate', 'DepScan')

    # Add interactive FAQ script inline
    faq_script = '''
    <script>
    function handleHeroSubmit(e) {
        if (e && e.preventDefault) e.preventDefault();
        const input = document.getElementById("hero-repo-url");
        if (!input) return false;
        const val = input.value.trim();
        if (!val) { input.focus(); return false; }
        window.location.href = "/dashboard?repo=" + encodeURIComponent(val);
        return false;
    }
    function fillAndSubmit(url) {
        const input = document.getElementById("hero-repo-url");
        if (input) input.value = url;
        window.location.href = "/dashboard?repo=" + encodeURIComponent(url);
    }
    document.addEventListener("DOMContentLoaded", () => {
        document.querySelectorAll(".faq-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                const ans = btn.parentElement.querySelector(".faq-ans");
                if (ans) ans.classList.toggle("hidden");
            });
        });
    });
    </script>
    '''
    html = html.replace('</body>', faq_script + '</body>')

    with open('frontend/landing.html', 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Successfully generated frontend/landing.html ({len(html)} bytes)")

if __name__ == "__main__":
    main()
