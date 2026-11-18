
const API = "http://127.0.0.1:8000/api/";

const button = document.getElementById("captureBtn");
const statusBox = document.getElementById("status");

function setStatus(message) {
    statusBox.textContent = message;
}

button.addEventListener("click", async () => {
    button.disabled = true;
    setStatus("Collecting performance data...");

    try {
        // 1. Get the currently active Chrome tab.
        const [tab] = await chrome.tabs.query({
            active: true,
            lastFocusedWindow: true
        });

        if (!tab) {
            throw new Error("Chrome could not find an active tab.");
        }

        if (tab.id === undefined) {
            throw new Error("Could not identify the active tab.");
        }

        if (!tab.url) {
            throw new Error(
                "Website URL unavailable. Open a normal website and try again."
            );
        }

        const pageURL = new URL(tab.url);

        if (!["http:", "https:"].includes(pageURL.protocol)) {
            throw new Error("Open a normal HTTP or HTTPS website first.");
        }

        // 2. Read Navigation Timing from the current page.
        const results = await chrome.scripting.executeScript({
            target: { tabId: tab.id },

            func: () => {
                const nav = performance.getEntriesByType(
                    "navigation"
                )[0];

                if (!nav) {
                    throw new Error("Navigation timing unavailable.");
                }

                function duration(start, end) {
                    if (end < start) {
                        return null;
                    }

                    return Math.round(end - start);
                }

                return {
                    dns: duration(
                        nav.domainLookupStart,
                        nav.domainLookupEnd
                    ),

                    tcp: duration(
                        nav.connectStart,
                        nav.connectEnd
                    ),

                    tls: nav.secureConnectionStart > 0
                        ? duration(
                            nav.secureConnectionStart,
                            nav.connectEnd
                        )
                        : null,

                    ttfb: duration(
                        nav.requestStart,
                        nav.responseStart
                    ),

                    page_load: nav.loadEventEnd > 0
                        ? Math.round(nav.loadEventEnd)
                        : null
                };
            }
        });

        const metrics = results[0].result;

        setStatus("Connecting to Django...");

        // 3. Retrieve existing websites.
        const websiteResponse = await fetch(
            API + "websites/"
        );

        if (!websiteResponse.ok) {
            throw new Error("Could not retrieve websites.");
        }

        const websites = await websiteResponse.json();

        // 4. Find or create the website.
        let website = websites.find(
            item => item.url === pageURL.origin
        );

        if (!website) {
            const createWebsite = await fetch(
                API + "websites/",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        name: pageURL.hostname,
                        url: pageURL.origin
                    })
                }
            );

            if (!createWebsite.ok) {
                const errorData = await createWebsite.json();

                throw new Error(
                    "Could not save website: " +
                    JSON.stringify(errorData)
                );
            }

            website = await createWebsite.json();
        }

        // 5. Create a website visit.
        const visitResponse = await fetch(
            API + "visits/",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    website: website.id,
                    page_url: tab.url
                })
            }
        );

        if (!visitResponse.ok) {
            const errorData = await visitResponse.json();

            console.error("Visit API Error:", errorData);

            throw new Error(
                "Could not save website visit: " +
                JSON.stringify(errorData)
            );
        }

        const visit = await visitResponse.json();

        // 6. Save individual performance metrics.
        const metricData = [
            { name: "DNS", value: metrics.dns },
            { name: "TCP", value: metrics.tcp },
            { name: "TLS", value: metrics.tls },
            { name: "TTFB", value: metrics.ttfb },
            { name: "Page Load", value: metrics.page_load }
        ];

        for (const metric of metricData) {
            if (metric.value === null) {
                continue;
            }

            const response = await fetch(
                API + "metrics/",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        visit: visit.id,
                        metric_name: metric.name,
                        value: metric.value,
                        unit: "ms"
                    })
                }
            );

            if (!response.ok) {
                let errorData;

                try{
                    errorData = await response.json();
                } catch {
                    errorData = "Server returned an invalid or non-JSON response.";
                }

                throw new Error(
                    "Failed to save " +
                    metric.name +
                    ": " +
                    JSON.stringify(errorData)
                );
            }
        }
        // Run diagnostics automatically after saving all metrics.
        const diagnosticResponse = await fetch(
            API + "visits/" + visit.id + "/diagnostics/",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({})
            }
        );

        if (!diagnosticResponse.ok) {
            let errorData;  

            try{
                errorData = await diagnosticResponse.json();
            } catch{
                errorData = "Server returned an invalid or non-JSON response.";
            }

            throw new Error(
                "Failed to run diagnostics: " +
                JSON.stringify(errorData)
            );
        }

        // 7. Display success message.
        setStatus(
            "Success! Performance data saved for " +
            pageURL.hostname
        );

    } catch (error) {
        console.error("NetScope error:", error);

        if (error.message === "Failed to fetch") {
            setStatus(
                "Connection Error: Cannot connect to NetScope server. Please start Django and try again."
            );
        } else{
            setStatus("Error: " + error.message);
        }
        

    } finally {
        button.disabled = false;
    }
});
