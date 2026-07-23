const { chromium } = require("playwright");

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  const web = "https://realmadrid.pl";

  await page.goto(web);

  await page.waitForTimeout(5000);

  await browser.close();
})();