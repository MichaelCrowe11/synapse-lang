"use strict";
const PYODIDE_URL = "https://cdn.jsdelivr.net/pyodide/v0.27.7/full/";
let engine, runtime;
async function initialize() {
  importScripts(PYODIDE_URL + "pyodide.js");
  const py = await loadPyodide({indexURL: PYODIDE_URL});
  self.postMessage({status: "Loading NumPy and SciPy for uncertainty propagation..."});
  await py.loadPackage(["numpy", "scipy"]);
  const response = await fetch("runtime.json");
  if (!response.ok) throw new Error("Runtime manifest unavailable");
  const manifest = await response.json();
  if (!/^synapse_lang-[0-9.]+-py3-none-any\.whl$/.test(manifest.wheel)) throw new Error("Invalid runtime manifest");
  const wheelResponse = await fetch(manifest.wheel);
  if (!wheelResponse.ok) throw new Error("Synapse wheel unavailable");
  const wheel = await wheelResponse.arrayBuffer();
  const hash = Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256", wheel)), (x) => x.toString(16).padStart(2, "0")).join("");
  if (hash !== manifest.sha256) throw new Error("Synapse wheel integrity check failed");
  py.unpackArchive(wheel, "zip", {extractDir: "/home/pyodide"});
  py.runPython("import json\nfrom synapse_lang.showcase import evaluate");
  runtime = {
    pyodide: "0.27.7", wheel: manifest.wheel, sha256: hash,
    ...JSON.parse(py.runPython("import sys, numpy, scipy\njson.dumps({'python': sys.version.split()[0], 'numpy': numpy.__version__, 'scipy': scipy.__version__})")),
  };
  return py;
}
self.onmessage = async ({data}) => {
  try {
    engine ||= initialize();
    const py = await engine;
    py.globals.set("request_json", JSON.stringify(data));
    const result = py.runPython("request = json.loads(request_json)\njson.dumps(evaluate(request['case'], request['parameters']), allow_nan=False)");
    self.postMessage({report: {...JSON.parse(result), runtime}});
  } catch (error) {
    const message = String(error.message || error).trim().split("\n").pop();
    self.postMessage({error: message.slice(0, 400)});
  }
};
