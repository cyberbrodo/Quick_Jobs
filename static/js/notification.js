const publicKey = "MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAECb41v72F2CfQHzrmUlRl5/4oApV70fuOxGWVqdtUG4kV61hivWuP57pC3AbL9qoLMX6+cj3/ZJwJ/M0SbaoIMQ==";

async function registerPush() {

    if (!("serviceWorker" in navigator)) return;

    if (!("PushManager" in window)) return;

    const permission = await Notification.requestPermission();

    if (permission !== "granted") return;

    const registration = await navigator.serviceWorker.register("/sw.js");

    let subscription = await registration.pushManager.getSubscription();

    if (!subscription) {

        subscription = await registration.pushManager.subscribe({

            userVisibleOnly: true,

            applicationServerKey: urlBase64ToUint8Array(publicKey)

        });

    }

    await fetch("/save-subscription/", {

        method: "POST",

        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },

        body: JSON.stringify(subscription)

    });

}

function urlBase64ToUint8Array(base64String) {

    const padding = "=".repeat((4 - base64String.length % 4) % 4);

    const base64 = (base64String + padding)
        .replace(/-/g, "+")
        .replace(/_/g, "/");

    const rawData = window.atob(base64);

    return Uint8Array.from([...rawData].map(c => c.charCodeAt(0)));

}

function getCookie(name) {

    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {

        const cookies = document.cookie.split(";");

        for (let cookie of cookies) {

            cookie = cookie.trim();

            if (cookie.startsWith(name + "=")) {

                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));

            }

        }

    }

    return cookieValue;

}

registerPush();