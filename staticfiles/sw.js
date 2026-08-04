self.addEventListener("install", event => {
    console.log("Service Worker Installed");
});

self.addEventListener("fetch", event => {});


self.addEventListener("push", function(event) {

    const data = event.data.json();

    self.registration.showNotification(data.title, {
        body: data.body,
        icon: "/static/icons/icon-192.png",
        badge: "/static/icons/icon-192.png",
        data: {
            url: data.url
        }
    });

});

self.addEventListener("notificationclick", function(event){

    event.notification.close();

    event.waitUntil(
        clients.openWindow(event.notification.data.url)
    );

});