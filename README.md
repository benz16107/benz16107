<!-- hero*.svg comes from scripts/hero.py and wins*.svg from scripts/wins.py, both run by hand. stats*.svg and
     live/ are redrawn daily by .github/workflows/stats.yml, from public commits and a request to each live
     site; each tile in live/ links to its site, so keep the tiles in step with SITES in scripts/stats.py.
     <picture> follows the viewer's GitHub theme. -->
<a href="https://thebenzhou.com"><picture><source media="(prefers-color-scheme: dark)" srcset="./hero-dark.svg" /><img src="./hero.svg" width="100%" alt="Ben Zhou. CS at the University of Toronto. I build things fast, ship them, and keep the ones that work. 24 projects in 2026, 15 hackathon wins, 9 live right now." /></picture></a>
<picture><source media="(prefers-color-scheme: dark)" srcset="./stats-dark.svg" /><img src="./stats.svg" width="100%" alt="Commits to public repositories over the last 12 months, by month, redrawn daily" /></picture>
<picture><source media="(prefers-color-scheme: dark)" srcset="./live/head-dark.svg" /><img src="./live/head.svg" width="100%" alt="Which of my nine live projects answered a request today, checked daily" /></picture>
<a href="https://gurtos.com"><picture><source media="(prefers-color-scheme: dark)" srcset="./live/gurtos-dark.svg" /><img src="./live/gurtos.svg" width="33.33%" alt="GurtOS" /></picture></a><a href="https://pixie-underwriting.vercel.app"><picture><source media="(prefers-color-scheme: dark)" srcset="./live/pixie-dark.svg" /><img src="./live/pixie.svg" width="33.33%" alt="Pixie" /></picture></a><a href="https://uoftime.com"><picture><source media="(prefers-color-scheme: dark)" srcset="./live/uoftime-dark.svg" /><img src="./live/uoftime.svg" width="33.33%" alt="UofTime" /></picture></a><a href="https://apps.apple.com/app/keypace/id6777376987?mt=12"><picture><source media="(prefers-color-scheme: dark)" srcset="./live/keypace-dark.svg" /><img src="./live/keypace.svg" width="33.33%" alt="Keypace" /></picture></a><a href="https://dataframe.space"><picture><source media="(prefers-color-scheme: dark)" srcset="./live/dataframe-dark.svg" /><img src="./live/dataframe.svg" width="33.33%" alt="DataFrame" /></picture></a><a href="https://tradex-six-dun.vercel.app"><picture><source media="(prefers-color-scheme: dark)" srcset="./live/tradex-dark.svg" /><img src="./live/tradex.svg" width="33.33%" alt="tradex" /></picture></a><a href="https://huggingface.co/spaces/crackedcity/app"><picture><source media="(prefers-color-scheme: dark)" srcset="./live/crackedcity-dark.svg" /><img src="./live/crackedcity.svg" width="33.33%" alt="Cracked City" /></picture></a><a href="https://routewatch-jn559.ondigitalocean.app"><picture><source media="(prefers-color-scheme: dark)" srcset="./live/routewatch-dark.svg" /><img src="./live/routewatch.svg" width="33.33%" alt="RouteWatch" /></picture></a><a href="https://rcventure.ca"><picture><source media="(prefers-color-scheme: dark)" srcset="./live/rcventureca-dark.svg" /><img src="./live/rcventureca.svg" width="33.33%" alt="rcventure.ca" /></picture></a>

<div align="center">

[![Portfolio](https://img.shields.io/badge/Portfolio-thebenzhou.com-000000?style=for-the-badge&logo=googlechrome&logoColor=white)](https://thebenzhou.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/-ben-zhou-/)
[![X](https://img.shields.io/badge/X-@benzhoudev-000000?style=for-the-badge&logo=x&logoColor=white)](https://x.com/benzhoudev)
[![Gmail](https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:benz16107@gmail.com)
[![Instagram](https://img.shields.io/badge/Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white)](https://www.instagram.com/_ben_zhou_/)

</div>

---

<details>
<summary><b>15 hackathon wins</b>, click for the 12 prizes with a public write-up</summary>
<br>

<picture><source media="(prefers-color-scheme: dark)" srcset="./wins-dark.svg" /><img src="./wins.svg" width="100%" alt="Hackathon prizes with a public write-up in 2026, stacked by month" /></picture>

| When | Hackathon | Project | Prize |
|---|---|---|---|
| Nov 2026 | HackUTD 2026 | [Tessera](https://devpost.com/software/bean-4970h3) | Spacetime track, 2nd place |
| Oct 2026 | Cal Hacks 13.0 | [GurtOS](https://devpost.com/software/gurtos) | Atlassian prize<br>Fetch.ai special recognition prize<br>MLH Best Use of Solana |
| Sep 2026 | Hack the North 2026 | [Pixie](https://devpost.com/software/pixie-8vlj7g) | Intact track<br>Federato track |
| Jul 2026 | cuHacking7 | [tradex](https://devpost.com/software/tradex-0efat7) | MLH Best Use of Solana |
| Mar 2026 | McGill AeroHacks | [OOPS](https://devpost.com/software/skygrid) | Best Use of MongoDB Atlas |
| Mar 2026 | GenAI Genesis | [Eco-Pulse](https://devpost.com/software/eco-pulse-fpbo15) | Top 2 teams, online |
| Mar 2026 | Hack Days in the 6ix | [Packwise](https://devpost.com/software/packwise-jmgtqi) | Runner up |
| Feb 2026 | Mac-a-thon | [BlindSpot](https://devpost.com/software/blindspot-zs7dwq) | MLH Best Use of ElevenLabs<br>Best Use of Backboard.io (GitCloud) |

</details>

<br>

| Project | What it is | Built with |
|---|---|---|
| **[GurtOS](https://gurtos.com)** | An operating system for AI agents, built solo at Cal Hacks 13.0, where it **won an Atlassian prize, a Fetch.ai special recognition prize and MLH's Best Use of Solana**. Each agent task runs as its own Linux user in its own copy of the files, keys stay in a vault the agent never sees, and spending over budget waits for your OK. Open source, installs from its own ISO. **[Demo video](https://youtu.be/rREjU2ddIyo)** · **[Code](https://github.com/benz16107/gurtos)** | `TypeScript` `Linux` `Swift` |
| **[Pixie](https://pixie-underwriting.vercel.app)** | An insurance risk engine built solo at Hack the North 2026, where it **won the Intact and Federato tracks**. Agents decide what to look up, code computes every score and price, and a sentence with a number the tools did not return is blocked. **[Demo video](https://youtu.be/O47V32zbv20)** | `Next.js` `FastAPI` `Expo` |
| **[UofTime](https://uoftime.com)** | A timetable builder for all three UofT campuses. Pick sections on a week grid, see the walk between classes on a map, subscribe from any calendar app. No account, the timetable lives in the link. It is also an MCP server, so Claude or ChatGPT can build one in conversation. | `React` `TypeScript` `MCP` |
| **[Keypace](https://apps.apple.com/app/keypace/id6777376987?mt=12)** | A native macOS typing test, live on the Mac App Store. Version 1.1 adds a menu bar quick test that opens from any app and a per key heatmap. | `Swift` `SwiftUI` |
| **[DataFrame](https://dataframe.space)** | A node based canvas where every node runs **real Python in your browser**. CPython via Pyodide, so there is no execution server and your code never leaves the tab. Built at DRHX. | `tldraw` `Pyodide` `FastAPI` |
| **[tradex](https://tradex-six-dun.vercel.app)** | A marketplace for the agent economy. Agents pay each other per call in USDC on Solana over x402. No accounts, no API keys, reputation earned on chain. | `Next.js` `Solana` `x402` |
| **[Cracked City](https://huggingface.co/spaces/crackedcity/app)** | Road damage triage for Toronto: what to fix first, and what it costs. I built the NVFP4 quantized Qwen3.6 27B checkpoint and the [311 filing pipeline](https://github.com/benz16107/311-request). | `NVFP4` `Qwen` `Playwright` |
| **[RouteWatch](https://routewatch-jn559.ondigitalocean.app)** | Tracks how long a drive *actually* takes over weeks, not in the moment. Public demo, no login. | `Node` `Google Maps` |
| **[rcventure.ca](https://rcventure.ca)** | The website for Rotman Commerce Venture Capital, the UofT club where I am Marketing Manager. Intro video, research library, a 3D partner globe and a "would you back it?" swipe game. | `Next.js` `Tailwind` `Motion` |

---

<h3 align="center">Also worth a look</h3>

<div align="center">

| | |
|---|---|
| **[BlindSpot](https://github.com/benz16107/BlindSpot)** | Walking navigation for blind and low vision users. Voice agent, live camera, obstacle detection with haptics. **[Demo film](https://youtu.be/gp-m_eguosk)** |
| **[Nova](https://github.com/benz16107/Nova)** | In room hotel voice concierge on the OpenAI Realtime API, with NFC activation and isolated per guest memory |
| **[Artifex](https://github.com/benz16107/Artifex)** | A product idea becomes a spec, then brand research, then concept images, then actual 3D meshes |
| **[Pentagon](https://github.com/benz16107/htf)** | Multi tenant supply chain risk platform built around explainable agent traces |

</div>

---

<h3 align="center">Languages and Tools</h3>

<p align="center">
  <a href="https://www.python.org" target="_blank"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" alt="python" width="42" height="42"/></a>&nbsp;&nbsp;
  <a href="https://www.typescriptlang.org/" target="_blank"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/typescript/typescript-original.svg" alt="typescript" width="42" height="42"/></a>&nbsp;&nbsp;
  <a href="https://developer.mozilla.org/en-US/docs/Web/JavaScript" target="_blank"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/javascript/javascript-original.svg" alt="javascript" width="42" height="42"/></a>&nbsp;&nbsp;
  <a href="https://developer.apple.com/swift/" target="_blank"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/swift/swift-original.svg" alt="swift" width="42" height="42"/></a>&nbsp;&nbsp;
  <a href="https://dart.dev" target="_blank"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/dart/dart-original.svg" alt="dart" width="42" height="42"/></a>&nbsp;&nbsp;
  <a href="https://www.java.com" target="_blank"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/java/java-original.svg" alt="java" width="42" height="42"/></a>&nbsp;&nbsp;
  <a href="https://www.postgresql.org" target="_blank"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/postgresql/postgresql-original.svg" alt="postgresql" width="42" height="42"/></a>
</p>

<p align="center">
  <a href="https://nextjs.org/" target="_blank"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/nextjs/nextjs-original.svg" alt="nextjs" width="42" height="42"/></a>&nbsp;&nbsp;
  <a href="https://reactjs.org/" target="_blank"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/react/react-original.svg" alt="react" width="42" height="42"/></a>&nbsp;&nbsp;
  <a href="https://nodejs.org" target="_blank"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/nodejs/nodejs-original.svg" alt="nodejs" width="42" height="42"/></a>&nbsp;&nbsp;
  <a href="https://fastapi.tiangolo.com/" target="_blank"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/fastapi/fastapi-original.svg" alt="fastapi" width="42" height="42"/></a>&nbsp;&nbsp;
  <a href="https://flutter.dev" target="_blank"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/flutter/flutter-original.svg" alt="flutter" width="42" height="42"/></a>&nbsp;&nbsp;
  <a href="https://tailwindcss.com/" target="_blank"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/tailwindcss/tailwindcss-original.svg" alt="tailwind" width="42" height="42"/></a>&nbsp;&nbsp;
  <a href="https://www.docker.com/" target="_blank"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/docker/docker-original.svg" alt="docker" width="42" height="42"/></a>
</p>

---

<h3 align="center">Away from the keyboard</h3>

<div align="center">

![Vancouver to Toronto](https://img.shields.io/badge/Vancouver,_BC_%E2%86%92_Toronto,_ON-C8102E?style=flat-square)

![Bodies](https://img.shields.io/badge/Sony-A7S_III_·_A1_II_·_A7R_V-FF6600?style=flat-square)
![Zooms](https://img.shields.io/badge/GM-24--70_·_70--200_·_50--150-1a1a1a?style=flat-square)
![Primes](https://img.shields.io/badge/GM-50mm_f%2F1.2-1a1a1a?style=flat-square)
![Long](https://img.shields.io/badge/G-200--600mm-1a1a1a?style=flat-square)
![Accessories](https://img.shields.io/badge/+_a_lot_of_other_accessories-6e6e6e?style=flat-square)

![BMW](https://img.shields.io/badge/BMW-2×_E93_N54_·_G12_N63-0166B1?style=flat-square)
![Printers](https://img.shields.io/badge/Printers-Bambu_Lab_H2D_·_Ender_3_Pro-00AE42?style=flat-square)

[Rotate my 3D printed business card](./card.stl) in GitHub's 3D viewer

</div>
