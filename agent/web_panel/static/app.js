const API_BASE = 'http://127.0.0.1:8181';

const statusTextEl = document.getElementById('status-text');
const logOutputEl = document.getElementById('log-output');

function appendLog(message) {
    const ts = new Date().toLocaleTimeString();
    logOutputEl.textContent = `[${ts}] ${message}\n` + logOutputEl.textContent;
}

function setStatus(text, isRunning = null) {
    statusTextEl.textContent = text;
    statusTextEl.classList.remove('status-running', 'status-stopped', 'status-unknown');

    if (isRunning === true) {
        statusTextEl.classList.add('status-running');
    } else if (isRunning === false) {
        statusTextEl.classList.add('status-stopped');
    } else {
        statusTextEl.classList.add('status-unknown');
    }
}

async function callEndpoint(path) {
    try {
        const resp = await fetch(`${API_BASE}${path}`, { cache: 'no-cache' });
        const text = await resp.text();
        appendLog(`${path} → ${resp.status}: ${text}`);

        if (path === '/status') {
            if (text.includes('not running')) {
                setStatus('не запущен', false);
            } else if (text.includes('running')) {
                setStatus('запущен', true);
            } else {
                setStatus('неизвестно', null);
            }
        }
    } catch (e) {
        appendLog(`${path} → ERROR: ${e}`);
        setStatus('ошибка соединения', null);
    }
}

function startServer() { callEndpoint('/start'); }
function stopServer() { callEndpoint('/stop'); }
function restartServer() { callEndpoint('/restart'); }
function checkStatus() { callEndpoint('/status'); }

document.getElementById('start-btn').onclick = startServer;
document.getElementById('stop-btn').onclick = stopServer;
document.getElementById('restart-btn').onclick = restartServer;
document.getElementById('refresh-status-btn').onclick = checkStatus;

window.addEventListener('load', () => {
    appendLog('Панель загружена.');
    checkStatus();
    setInterval(checkStatus, 2000);
});
