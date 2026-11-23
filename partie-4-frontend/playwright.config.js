import { defineConfig } from '@playwright/test'
export default defineConfig({
  testDir:'./tests', testMatch:'app.spec.js', timeout:30000, fullyParallel:false, workers:1,
  reporter:[['list'],['json',{outputFile:'../commun/docs/verification/browser-results.json'}]],
  use:{baseURL:process.env.SAWTNA_WEB_URL||'http://127.0.0.1:5175',channel:process.env.SAWTNA_BROWSER_CHANNEL||undefined,viewport:{width:1440,height:1000},screenshot:'only-on-failure'},
})
