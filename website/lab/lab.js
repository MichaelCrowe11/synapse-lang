"use strict";
const $ = (id) => document.getElementById(id);
const examples = {
  concentration: {
    description: "How do independent measurement errors affect a concentration calculation?",
    fields: [["mass", "Mass (mg)", 10, 0, 1e6], ["mass_uncertainty", "Mass uncertainty, 1 SD (mg)", .1, 0, 1e5], ["volume", "Volume (mL)", 2, .000001, 1e6], ["volume_uncertainty", "Volume uncertainty, 1 SD (mL)", .02, 0, 1e5], ["target_relative_sd_percent", "Target relative standard deviation (%)", 5, .1, 100]],
  },
  spend: {
    description: "Explore an illustrative token budget. These are editable example rates, not live prices or invoice amounts.",
    fields: [["requests", "Expected requests", 10000, 0, 1e9], ["requests_uncertainty", "Request uncertainty, 1 SD", 1000, 0, 1e8], ["input_tokens", "Input tokens per request", 2000, 0, 1e6], ["output_tokens", "Output tokens per request", 500, 0, 1e6], ["input_rate", "USD per million input tokens", 1, 0, 1e4], ["output_rate", "USD per million output tokens", 4, 0, 1e4]],
  },
  bell: {
    description: "Simulate two entangled qubits: H on qubit 0, then CNOT. Measurements should be 00 or 11, not independent outcomes.",
    fields: [["shots", "Measurement shots", 1024, 64, 8192], ["seed", "Random seed", 42, 0, 2147483647]],
  },
};
let worker, timer, latest, ready = false;
function form() {
  const selected = examples[$("case").value];
  $("description").textContent = selected.description;
  $("fields").replaceChildren();
  for (const [name, title, value, min, max] of selected.fields) {
    const label = document.createElement("label"); label.htmlFor = name; label.textContent = title;
    const input = document.createElement("input");
    Object.assign(input, {id: name, name, type: "number", value, min, max, step: $("case").value === "bell" ? "1" : "any", required: true});
    $("fields").append(label, input);
  }
  if ($("case").value === "concentration") {
    const label = document.createElement("label");
    label.htmlFor = "method"; label.textContent = "Uncertainty method";
    const select = document.createElement("select"); select.id = "method";
    for (const [value, text] of [["first_order", "First-order propagation (small relative errors)"], ["lognormal", "Exact lognormal ratio (positive, independent inputs)"]]) {
      const option = document.createElement("option"); option.value = value; option.textContent = text; select.append(option);
    }
    $("fields").prepend(label, select);
    const help = document.createElement("p");
    help.id = "volume-help"; help.className = "note";
    $("volume_uncertainty").setAttribute("aria-describedby", help.id);
    $("fields").appendChild(help);
    const targetHelp = document.createElement("p"); targetHelp.id = "target-help"; targetHelp.className = "note";
    targetHelp.textContent = "Planning target = output standard deviation / output mean. The initial 5% is an editable example, not an industry or clinical standard. Uncertainty inputs are 1 SD, not minimum/maximum bounds.";
    $("target_relative_sd_percent").setAttribute("aria-describedby", targetHelp.id);
    $("fields").appendChild(targetHelp);
  }
  clearResult();
  validateVolume();
  $("status").className = "";
  $("status").textContent = "Ready. Edit the example inputs, then run.";
}
function validateVolume() {
  if ($("case").value !== "concentration") return true;
  const volume = $("volume").valueAsNumber;
  const input = $("volume_uncertainty");
  const lognormal = $("method").value === "lognormal";
  const limit = Math.min(100000, volume * 0.1);
  const validVolume = Number.isFinite(volume) && volume > 0;
  const displayLimit = validVolume ? Number(limit.toPrecision(10)).toString() : "";
  const exceeds = !lognormal && validVolume && input.valueAsNumber > limit;
  input.max = !lognormal && validVolume ? String(limit) : "100000";
  $("mass").min = lognormal ? "0.000001" : "0";
  const message = exceeds ? `First-order propagation accepts at most ${displayLimit} mL uncertainty (10% of volume). Keep your measured uncertainty: choose exact lognormal analysis only if that positive, independent-input model fits your data.` : "";
  input.setCustomValidity(message);
  input.setAttribute("aria-invalid", String(exceeds));
  $("volume-help").textContent = lognormal
    ? "Model assumption: mass and volume are independent positive lognormal variables. Enter arithmetic means and standard deviations. The result includes an asymmetric 95% model coverage interval, not a clinical confidence interval. A mean and SD alone do not establish this distribution."
    : validVolume ? `First-order volume uncertainty limit: ${displayLimit} mL (10%). For larger errors, choose a suitable distribution model; do not shrink the reported uncertainty.` : "Enter a positive volume.";
  if (exceeds) { $("status").className = "error"; $("status").textContent = message; }
  return !exceeds;
}
function clearResult() {
  latest = null; $("export").disabled = true;
  $("insights").hidden = true;
  for (const id of ["meaning", "precision-status", "contribution-basis", "contributions", "requirements", "scenarios", "planning-note"]) $(id).replaceChildren();
  $("result").textContent = "Run with these inputs to calculate a result.";
  $("bars").replaceChildren(); $("provenance").textContent = ""; $("analysis").textContent = "";
  $("source").textContent = "Run an experiment to inspect its exact source.";
  $("assumptions").replaceChildren();
}
function busy(value) {
  $("run").disabled = value; $("case").disabled = value; $("stop").hidden = !value;
  $("fields").querySelectorAll("input, select").forEach((input) => { input.disabled = value; });
  if (!value) { clearTimeout(timer); $("run").textContent = ready ? "Run calculation" : "Load engine & run"; }
}
function stop(message) {
  if (worker) worker.terminate();
  worker = undefined; ready = false; busy(false);
  $("status").textContent = message;
}
function show(report) {
  latest = report; $("export").disabled = false;
  const result = report.result;
  if (result.counts) {
    $("result").textContent = `${result.shots.toLocaleString()} simulated measurements`;
    for (const state of ["00", "01", "10", "11"]) {
      const row = document.createElement("div"); row.className = "bar-row";
      const label = document.createElement("span"); label.textContent = state;
      const bar = document.createElement("progress"); bar.max = result.shots; bar.value = result.counts[state] || 0; bar.setAttribute("aria-label", `State ${state}`);
      const count = document.createElement("span"); count.textContent = `${bar.value} (${(100 * bar.value / bar.max).toFixed(1)}%)`;
      row.append(label, bar, count); $("bars").append(row);
    }
  } else if (report.method === "lognormal") {
    const fmt = (n) => new Intl.NumberFormat(undefined, {maximumSignificantDigits: 6}).format(n);
    $("result").textContent = `Mean ${fmt(result.mean)} ${report.unit}`;
    for (const text of [
      `95% model coverage: ${fmt(result.interval.lower)} to ${fmt(result.interval.upper)} ${report.unit}`,
      `Median ${fmt(result.median)}; standard deviation ${fmt(result.standard_deviation)} ${report.unit}`,
      `Ratio of input means: ${fmt(result.nominal_ratio)} ${report.unit} (not the distribution mean)`,
    ]) {
      const line = document.createElement("p"); line.textContent = text; $("bars").append(line);
    }
  } else {
    const fmt = (n) => new Intl.NumberFormat(undefined, {maximumSignificantDigits: 6}).format(n);
    $("result").textContent = `${fmt(result.nominal)} ± ${fmt(result.uncertainty)} ${report.unit}`;
  }
  showInsights(report);
  $("source").textContent = report.source;
  $("analysis").textContent = report.analysis;
  $("assumptions").replaceChildren(...report.assumptions.map((text) => { const li = document.createElement("li"); li.textContent = text; return li; }));
  $("provenance").textContent = `${report.engine} ${report.version} / ${report.method} / Python in WebAssembly / ${report.timestamp}`;
}
function showInsights(report) {
  if (!report.insights) return;
  const insights = report.insights;
  const fmt = (n) => new Intl.NumberFormat(undefined, {maximumSignificantDigits: 4}).format(n);
  const percent = (n) => `${fmt(n * 100)}%`;
  $("insights").hidden = false;
  $("meaning").textContent = insights.summary;
  if (!insights.available) return;
  if (report.method === "lognormal") {
    $("meaning").textContent += " The mean averages over the modeled outcomes; the median splits them in half. Dividing by smaller possible volumes stretches the upper tail, so the mean can exceed the ratio of input means. The 95% interval describes this model's outcomes, not certainty about a real sample.";
  } else {
    $("meaning").textContent += " The ± value is one propagated standard deviation, not a guaranteed range or a 95% interval.";
  }
  $("precision-status").textContent = `${percent(insights.relative_sd)} relative SD / ${percent(insights.target_relative_sd)} target: ${insights.meets_target ? "numerical target met" : "above target"}`;
  $("contribution-basis").textContent = `Contribution basis: ${insights.contributions.basis}. These are not probabilities of an input being wrong.`;
  for (const name of ["mass", "volume"]) {
    const share = insights.contributions.shares[name];
    const row = document.createElement("div"); row.className = "contribution-row";
    const label = document.createElement("span"); label.textContent = name === "mass" ? "Mass" : "Volume";
    const bar = document.createElement("progress"); bar.max = 1; bar.value = share; bar.setAttribute("aria-label", `${label.textContent} variance contribution`);
    const amount = document.createElement("span"); amount.textContent = percent(share);
    row.append(label, bar, amount); $("contributions").append(row);
  }
  for (const requirement of insights.requirements) {
    const card = document.createElement("p"); card.className = "requirement";
    const name = requirement.input === "mass" ? "Mass" : "Volume";
    const other = requirement.input === "mass" ? "volume" : "mass";
    if (requirement.status === "unreachable_alone") {
      card.textContent = `${name} alone cannot meet the target: the unchanged ${other} uncertainty already exceeds it, even if ${requirement.input} SD were zero.`;
    } else if (requirement.status === "already_sufficient") {
      card.textContent = `${name}: current SD ${fmt(requirement.current_sd)} ${requirement.unit} already satisfies the target with the other input unchanged.`;
    } else {
      card.textContent = `${name}: achieve SD of at most approximately ${fmt(requirement.max_sd)} ${requirement.unit}, compared with ${fmt(requirement.current_sd)} ${requirement.unit} now, while keeping ${other} unchanged.`;
    }
    if (requirement.first_order_guard_max_sd !== null) card.textContent += ` This demo's first-order volume limit of ${fmt(requirement.first_order_guard_max_sd)} mL also applies.`;
    $("requirements").append(card);
  }
  for (const scenario of insights.scenarios) {
    const card = document.createElement("article"); card.className = "scenario";
    const heading = document.createElement("h4"); heading.textContent = scenario.label;
    const inputs = document.createElement("p"); inputs.className = "note";
    inputs.textContent = `Mass SD ${fmt(scenario.mass_sd)} mg; volume SD ${fmt(scenario.volume_sd)} mL`;
    const metric = document.createElement("p"); metric.className = "scenario-metric";
    metric.textContent = `${percent(scenario.relative_sd)} relative SD`;
    const outcome = document.createElement("p"); outcome.className = "note";
    outcome.textContent = scenario.meets_target ? "Meets your numerical target" : "Still above your numerical target";
    card.append(heading, inputs, metric, outcome);
    if (scenario.result.interval) {
      const interval = document.createElement("p"); interval.className = "note";
      interval.textContent = `95% model coverage: ${fmt(scenario.result.interval.lower)} to ${fmt(scenario.result.interval.upper)} ${report.unit}`;
      card.append(interval);
    }
    $("scenarios").append(card);
  }
  $("planning-note").textContent = `${insights.planning_note} Target equation: ${insights.target_equation}.`;
}
$("case").addEventListener("change", form);
$("experiment").addEventListener("input", () => {
  clearResult();
  if (validateVolume()) {
    $("status").className = "";
    $("status").textContent = "Inputs changed. Run to calculate a new result.";
  }
});
$("experiment").addEventListener("invalid", (event) => {
  $("status").className = "error";
  const label = event.target.labels?.[0]?.textContent || "Input";
  $("status").textContent = `${label}: ${event.target.validationMessage}`;
}, true);
$("experiment").addEventListener("submit", (event) => {
  event.preventDefault();
  if (!validateVolume() || !$("experiment").reportValidity()) return;
  clearResult(); busy(true); $("status").className = "";
  $("status").textContent = ready ? "Calculating locally..." : "Loading the real Python engine. First load may take a minute...";
  const parameters = {};
  for (const [name] of examples[$("case").value].fields) parameters[name] = Number($(name).value);
  if ($("case").value === "concentration") parameters.method = $("method").value;
  if (!worker) {
    worker = new Worker("worker.js");
    worker.onmessage = ({data}) => {
      if (data.status) { $("status").textContent = data.status; return; }
      if (data.error) { $("status").className = "error"; stop(`Calculation failed: ${data.error}`); return; }
      ready = true; show(data.report); busy(false); $("status").textContent = "Completed locally. No model calls made.";
    };
    worker.onerror = () => { $("status").className = "error"; stop("Engine could not load. Check the network connection and browser support, then retry."); };
  }
  timer = setTimeout(() => { $("status").className = "error"; stop("Engine timed out and was stopped. Check your connection, then retry."); }, 180000);
  worker.postMessage({case: $("case").value, parameters});
});
$("stop").addEventListener("click", () => stop("Stopped. No result was saved."));
$("export").addEventListener("click", () => {
  if (!latest) return;
  const blob = new Blob([JSON.stringify(latest, null, 2) + "\n"], {type: "application/json"});
  const url = URL.createObjectURL(blob), link = document.createElement("a");
  link.href = url; link.download = `synapse-${latest.case}.json`; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
});
window.addEventListener("pagehide", () => stop("Page suspended. Run again to restart the engine."));
form();
