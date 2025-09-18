#!/usr/bin/env node
const { spawn } = require('child_process');
const path = require('path');

const args = process.argv.slice(2);
const synapseCmd = spawn('python', ['-m', 'synapse_lang', ...args], {
    stdio: 'inherit',
    shell: true
});

synapseCmd.on('close', (code) => {
    process.exit(code);
});
