// require fs and puppeteer
const argparse = require("argparse");
const fs = require("fs");
const puppeteer = require("puppeteer");
const path = require('path')
const express = require('express')


function parseArgs() {
  const parser = new argparse.ArgumentParser({
    description: `
      Spin up the Nextstrain forecasts-ncov viz app to capture screenshots of
      the D3 visualizations for model results.
    `,
  });

  parser.add_argument("--output-dir", {
    default: "figures",
    dest: "outputDir",
    help: "Output directory for screenshots."
  });

  return parser.parse_args();
}

/**
 * These are the IDs of the DOM elements which
 * we will take screenshots of
 */
const elementsToScreenshot = [
  "cladeFrequenciesPanel",
  "cladeGrowthAdvantagePanel",
  "lineageFrequenciesPanel",
  "lineageGrowthAdvantagePanel",
];

const resolutions = [
  {width: 720, name: 'small'}, // 2-wide
  {width: 1000, name: 'medium'}, // 3-wide
  // {width: 1200, name: '...'}, // 3-wide with side legend
  {width: 1300, name: 'large'}, // 4-wide
  {width: 1550, name: 'xlarge'} // 5-wide
]

async function captureScreenshot(dir) {

  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir);
  }

  let browser = null;
  let failure;

  try {
    browser = await puppeteer.launch({ headless: true });

    const page = await browser.newPage();

    await page.setViewport({ width: 1440, height: 1080 });

    await page.goto("http://localhost:3000/forecasts-ncov/");

    await page.waitForSelector('#cladeFrequenciesPanel', {visible: true})
    await page.waitForSelector('svg', {visible: true})
    await page.waitForTimeout(700); // ensure it's painted -- may not be necessary?
    console.log("Page, including SGVs, rendered")
    await removeLogitToggle(page, '#cladeFrequenciesPanel');
    await removeLogitToggle(page, '#lineageFrequenciesPanel');


    for (const resolution of resolutions) {
      await page.setViewport({ width: resolution.width, height: 1080 });
      await page.waitForTimeout(700); // the library has a 500ms debounce when listening to window resizes
      /* save each panel (of small multiples) as a .png image */
      console.log(`Finding & saving panels at size ${resolution.name} (page width of ${resolution.width}px)`);
      for (const id of elementsToScreenshot) {
        const panel = await page.$(`#${id}`);
        const figureWidth = Math.floor((await panel.boundingBox()).width);
        const fname = `${dir}/${id}_${resolution.name}.png`
        await panel.screenshot({ path: fname }); 
        console.log(`\t${fname} (width: ${figureWidth}px)`)
      }
    }
  } catch (err) {
    console.log(`❌ Error: ${err.message}`);
    failure = true; // to be handled in the `finally` block
  } finally {
    await browser.close();
    failure ? process.exit(2) : console.log(`\n🎉 success`);
  }
}

async function startServer() {
  const app = express()
  app.set('port', 3000);
  app.use("/forecasts-ncov", express.static(path.join(__dirname, '..', "dist")))
  const server = await app.listen(app.get('port'));
  console.log(`Ephemeral server running at port ${app.get('port')}`)
  return server;
}

async function main({outputDir}) {
  const server = await startServer();
  await captureScreenshot(outputDir);
  server.close();
}

async function removeLogitToggle(page, parentID) {
  console.log("Removing logit toggle prior to screenshots")
  try {
    await page.evaluate((parentID) => {
      /* Structure is:
      <div id="cladeFrequenciesPanel">
        <div>
          <div>TOGGLE HERE</div>
          <div>Panels, Legend</div>
        </div>
      </div>
      */
      // NOTE: this function is called in the page's context, so you
      // don't have access to variables outside this function's scope
      document.querySelector(parentID).children[0].children[0].remove()
    }, parentID)
    console.log("\tSuccess")
  } catch (err) {
    console.error(err)
    console.log("Logit toggle removal failed. We'll keep going as updated screenshots with the toggle are better than stale screenshots.")
  }
}

main(parseArgs());

