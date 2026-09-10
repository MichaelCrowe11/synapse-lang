"""Exercise the actual Pyodide Lab and failure recovery against a local server."""
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

from playwright.sync_api import expect, sync_playwright


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="Local website /lab/ URL")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "results.json").write_text(json.dumps({"status": "running"}) + "\n")
    checks = []

    def run(page):
        page.locator("#run").click()
        expect(page.locator("#status")).to_have_text(
            re.compile("Completed|failed|could not|timed out"), timeout=180000
        )
        expect(page.locator("#status")).to_have_text("Completed locally. No AI tokens used.")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(accept_downloads=True, viewport={"width": 1440, "height": 1000})
        page = context.new_page()
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(args.url)
        run(page)
        expect(page.locator("#result")).to_have_text("5 ± 0.0707107 mg/mL")
        checks.append("real Pyodide default concentration")
        page.locator("#volume_uncertainty").fill("1")
        expect(page.locator("#volume_uncertainty")).to_have_attribute("aria-invalid", "true")
        expect(page.locator("#export")).to_be_disabled()
        expect(page.locator("#status")).to_contain_text("Keep your measured uncertainty")
        checks.append("first-order guard and stale export invalidation")
        page.locator("#method").select_option("lognormal")
        expect(page.locator("#volume_uncertainty")).to_have_value("1")
        expect(page.locator("#volume_uncertainty")).to_have_attribute("aria-invalid", "false")
        run(page)
        expect(page.locator("#result")).to_have_text("Mean 6.25 mg/mL")
        expect(page.locator("#bars")).to_contain_text("2.21423 to 14.1119")
        expect(page.locator("#analysis")).to_contain_text("Python math and SciPy")
        checks.append("explicit nonlinear method with unchanged uncertainty")
        expect(page.locator("#insights")).to_be_visible()
        expect(page.locator("#meaning")).to_contain_text("Volume is the larger uncertainty contributor")
        expect(page.locator("#contribution-basis")).to_contain_text("variance of log(concentration)")
        expect(page.locator("#requirements")).to_contain_text("0.09797 mL")
        expect(page.locator("#requirements")).to_contain_text("Mass alone cannot meet the target")
        expect(page.locator("#scenarios .scenario")).to_have_count(5)
        expect(page.locator("#scenarios .scenario").last).to_contain_text("Volume SD at target")
        expect(page.locator("#scenarios .scenario").last).to_contain_text("Meets your numerical target")
        expect(page.locator("#volume_uncertainty")).to_have_value("1")
        checks.append("uncertainty attribution, inverse precision target and five what-if scenarios")
        page.locator("#target_relative_sd_percent").fill("60")
        expect(page.locator("#insights")).to_be_hidden()
        expect(page.locator("#export")).to_be_disabled()
        run(page)
        expect(page.locator("#precision-status")).to_contain_text("numerical target met")
        expect(page.locator("#result")).to_have_text("Mean 6.25 mg/mL")
        page.locator("#target_relative_sd_percent").fill("0")
        page.locator("#run").click()
        expect(page.locator("#status")).to_have_class("error")
        page.locator("#target_relative_sd_percent").fill("5")
        run(page)
        checks.append("target validation and edits affect planning, not observations")
        with page.expect_download() as download:
            page.locator("#export").click()
        download.value.save_as(args.output / "concentration.json")
        report = json.loads((args.output / "concentration.json").read_text())
        assert report["insights"]["contributions"]["dominant"] == "volume"
        assert len(report["insights"]["scenarios"]) == 5
        assert report["insights"]["requirements"][1]["max_sd"] < 0.098
        assert report["method"] == "lognormal"
        assert report["inputs"]["volume_uncertainty"] == 1
        assert math.isclose(report["result"]["mean"], 6.25)
        assert report["runtime"]["pyodide"] == "0.27.7"
        assert len(report["runtime"]["sha256"]) == 64
        checks.append("JSON download with method, inputs, versions and artifact digest")
        page.screenshot(path=str(args.output / "desktop.png"), full_page=True)

        page.locator("#mass").fill("0")
        page.locator("#run").click()
        expect(page.locator("#status")).to_have_class("error")
        expect(page.locator("#export")).to_be_disabled()
        page.locator("#mass").fill("10")
        run(page)
        page.locator("#method").select_option("first_order")
        expect(page.locator("#volume_uncertainty")).to_have_attribute("aria-invalid", "true")
        page.locator("#volume_uncertainty").fill("0.02")
        run(page)
        expect(page.locator("#result")).to_have_text("5 ± 0.0707107 mg/mL")
        checks.append("invalid mass and method-switch recovery")

        page.locator("#mass").fill("0")
        run(page)
        expect(page.locator("#meaning")).to_contain_text("absolute-error target")
        expect(page.locator("#scenarios .scenario")).to_have_count(0)
        page.locator("#mass").fill("0.0000000001")
        run(page)
        expect(page.locator("#meaning")).to_contain_text("near-zero")
        checks.append("zero and near-zero mass avoid misleading relative precision claims")
        page.locator("#case").select_option("spend")
        expect(page.locator("#insights")).to_be_hidden()
        run(page)
        expect(page.locator("#result")).to_have_text("40 ± 4 USD")
        page.locator("#input_rate").fill("")
        page.locator("#run").click()
        expect(page.locator("#status")).to_have_class("error")
        page.locator("#input_rate").fill("1")
        page.locator("#requests").fill("20000")
        run(page)
        expect(page.locator("#result")).to_have_text("80 ± 4 USD")
        checks.append("spend forecast and empty-input recovery")
        page.locator("#case").select_option("bell")
        run(page)
        first = page.locator("#bars").inner_text()
        run(page)
        assert page.locator("#bars").inner_text() == first
        expect(page.locator("#result")).to_have_text("1,024 simulated measurements")
        checks.append("seeded Bell simulation repeatability")

        # A mobile Chromium viewport is not native Safari or an installed app test.
        page.set_viewport_size({"width": 440, "height": 956})
        page.locator("#case").select_option("concentration")
        page.locator("#method").select_option("lognormal")
        page.locator("#volume_uncertainty").fill("1")
        run(page)
        assert page.evaluate("() => document.documentElement.scrollWidth <= window.innerWidth")
        page.screenshot(path=str(args.output / "mobile-viewport.png"), full_page=True)
        checks.append("440px mobile layout and calculation without horizontal overflow")
        page.set_viewport_size({"width": 375, "height": 812})
        assert page.evaluate("() => document.documentElement.scrollWidth <= window.innerWidth")
        expect(page.locator("#requirements")).to_be_visible()
        page.screenshot(path=str(args.output / "small-mobile.png"), full_page=True)
        checks.append("375px layout retains explanations and precision planning")

        # Cancel during cold initialization, then restart with a fresh worker.
        page.reload()
        page.locator("#run").click()
        page.locator("#stop").click()
        expect(page.locator("#status")).to_have_text("Stopped. No result was saved.")
        expect(page.locator("#export")).to_be_disabled()
        run(page)
        checks.append("cold-load cancellation and restart")

        # Simulate the browser back/forward cache lifecycle, not just navigation.
        page.evaluate("() => window.dispatchEvent(new Event('pagehide'))")
        run(page)
        checks.append("page suspension and engine restart")

        # Fault injection stays on the local static server; never alters a live endpoint.
        def corrupt_manifest(route):
            response = route.fetch()
            manifest = response.json()
            manifest["sha256"] = "0" * 64
            route.fulfill(response=response, json=manifest)

        context.route("**/runtime.json", corrupt_manifest)
        page.reload()
        page.locator("#run").click()
        expect(page.locator("#status")).to_contain_text("integrity check failed", timeout=180000)
        assert "Traceback" not in page.locator("#status").inner_text()
        expect(page.locator("#export")).to_be_disabled()
        context.unroute("**/runtime.json", corrupt_manifest)
        run(page)
        checks.append("wheel tampering fails closed and retry recovers")

        def missing_manifest(route):
            route.fulfill(status=503, body="Temporarily unavailable")

        context.route("**/runtime.json", missing_manifest)
        page.reload()
        page.locator("#run").click()
        expect(page.locator("#status")).to_contain_text("Runtime manifest unavailable", timeout=180000)
        context.unroute("**/runtime.json", missing_manifest)
        run(page)
        checks.append("unavailable runtime and retry recovery")
        # Bypass form validation to prove that the Python boundary still rejects bad data.
        page.evaluate("() => worker.postMessage({case: 'concentration', parameters: {volume: 0}})")
        expect(page.locator("#status")).to_contain_text("volume must be between", timeout=30000)
        assert "Traceback" not in page.locator("#status").inner_text()
        run(page)
        checks.append("Python boundary validation returns concise errors and recovers")

        def block_cdn(route):
            route.abort("internetdisconnected")

        context.route("https://cdn.jsdelivr.net/**", block_cdn)
        page.reload()
        page.locator("#run").click()
        expect(page.locator("#status")).to_contain_text("Calculation failed", timeout=30000)
        expect(page.locator("#run")).to_be_enabled()
        context.unroute("https://cdn.jsdelivr.net/**", block_cdn)
        run(page)
        checks.append("CDN network failure and retry recovery")

        # Shorten only the application's watchdog, not the browser's test assertions.
        page.evaluate("""() => {
            const original = window.setTimeout;
            window.setTimeout = (fn, ms, ...args) => original(fn, ms === 180000 ? 1 : ms, ...args);
        }""")
        page.evaluate("() => window.dispatchEvent(new Event('pagehide'))")
        page.locator("#run").click()
        expect(page.locator("#status")).to_contain_text("Engine timed out", timeout=10000)
        expect(page.locator("#run")).to_be_enabled()
        page.reload()
        run(page)
        checks.append("watchdog terminates stalled work and allows restart")
        assert not errors, errors
        checks.append("no uncaught page errors")
        (args.output / "results.json").write_text(json.dumps({
            "status": "passed", "browser": "Chromium", "checks": checks,
            "native_iphone_verified": False, "installed_apps_verified": False,
        }, indent=2) + "\n")
        browser.close()
    print(json.dumps({"status": "passed", "checks": len(checks)}, indent=2))


if __name__ == "__main__":
    main()
