async function getStatus() {
    try {
        const response = await fetch("http://127.0.0.1:5005/status");
        const data = await response.json();
        document.getElementById("status").innerText = data.status;
    } catch (error) {
        document.getElementById("status").innerText = "ошибка соединения";
    }
}

document.getElementById("btnStart").addEventListener("click", async () => {
    await fetch("http://127.0.0.1:5005/start");
    getStatus();
});

document.getElementById("btnStop").addEventListener("click", async () => {
    await fetch("http://127.0.0.1:5005/stop");
    getStatus();
});

document.getElementById("btnRestart").addEventListener("click", async () => {
    await fetch("http://127.0.0.1:5005/restart");
    getStatus();
});

document.getElementById("btnUpdate").addEventListener("click", getStatus);

window.onload = getStatus;
