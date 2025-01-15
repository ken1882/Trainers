// ==UserScript==
// @name         Neopets Captcha Image Collector
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  Automatically grab Neopets captcha images and save them for analysis
// @author       YourName
// @match        https://www.neopets.com/haggle.phtml
// @match        https://www.neopets.com/haggle.phtml*
// @grant        GM_download
// @run-at       document-idle
// ==/UserScript==

(function() {
    'use strict';

    // Function to detect and save the captcha image
    function saveCaptchaImage() {
        // Look for the captcha image element
        const captchaImage = document.querySelector('input[type="image"][src*="/captcha_show.phtml"]');

        if (captchaImage) {
            // Construct the full URL for the captcha image
            const captchaSrc = new URL(captchaImage.src, window.location.origin).href;

            if (captchaSrc) {
                console.log("Captcha image URL detected:", captchaSrc);

                // Download the captcha image using GM_download
                GM_download({
                    url: captchaSrc,
                    name: `neopets_captcha_${Date.now()}.png`,
                    onload: () => console.log("Captcha image saved successfully."),
                    onerror: (err) => console.error("Failed to save captcha image:", err)
                });
            }
        } else {
            console.log("Captcha image not found on this page.");
        }
    }

    // Run the function after the page fully loads
    window.addEventListener('load', saveCaptchaImage);
})();
