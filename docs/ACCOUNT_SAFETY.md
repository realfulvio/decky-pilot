# Account safety and anti-cheat assessment

Reviewed 17 October 2026. This is an engineering risk assessment, not legal advice or a guarantee from Valve, a game publisher or an anti-cheat vendor. Valve does not publish what VAC detects, and each game sets its own rules.

## Two separate risks

1. **Technical detection.** Anti-cheat looks for software that reads or writes game memory, injects code into the game process, hooks its rendering, or automates input. Valve's VAC FAQ describes cheats as third-party modifications that give an advantage, including changes to a game's executables and libraries. Community and vendor sources consistently put the detection line at injection, memory reads and input automation, not at reading the screen. Overlays have caused false positives in some titles, though.
2. **Rules.** The [Steam Subscriber Agreement](https://store.steampowered.com/subscriber_agreement/) §4.B defines Cheats as functionality that may give a player "an unfair competitive advantage when playing multiplayer versions" of content. It forbids using them, interfering with anti-cheat, and tampering with the execution of Steam. §4.C forbids bots, scripts and macros. §4.D allows automated detection plus human review, and account restriction. Games add their own terms; for example, [Embark's anti-cheat FAQ](https://id.embark.games/the-finals/support/faq/44-anti-cheat-policy-faq) allows overlays or game assistants "only if they do not interfere with gameplay or offer unfair advantages".

An AI assistant that touches nothing in the game can still break rule 2 when it gives live tactical help in competitive multiplayer. That is the main product risk, more than technical detection.

## What Decky Pilot does and does not do

| Vector | Decky Pilot | Risk |
|---|---|---|
| Game memory read/write, DLL/`.so` injection, render hooks | Never. Runs as a separate native Linux process under Decky with the `deck` UID. It never opens the game process, its files or its Proton prefix. | None from Decky Pilot |
| Input to the game | Never sends keys, buttons, mouse or controller input; no macros or automation. | None |
| Drawing over the game surface | No in-game overlay. Answers appear in Decky's own Quick Access Menu and Steam toasts. | Low |
| Screen image | Today only manual import of an image the player chose. Planned capture would use Valve's own compositor command (`gamescopectl screenshot`), the same layer as Steam screenshots, never the game's memory. Disabled until DP-016 is safe. | Low technically; see rules |
| Game identification | Reads the running app ID that Steam already exposes to its UI; read-only. | Low |
| Steam client | Runs inside Decky Loader, which itself injects into Steam's UI (CEF). Decky Pilot adds no further client modification. | Inherited from Decky (see below) |
| Network | Talks only to the AI service the player chose. Never to Steam, its Web API or the game's servers. | None |
| Proton anti-cheat (EAC/BattlEye) | These run inside the game's Wine/Proton environment. Decky Pilot is a native process outside it and never enters the prefix. Kernel anti-cheats (for example Vanguard) do not run on SteamOS. | Low, inferred, not vendor-confirmed |

**Inherited Decky risk.** Strictly, Decky Loader modifies how the Steam client UI runs, which §4.B mentions ("tamper with the execution of Steam"). It is widely used, and we found no documented VAC or account ban caused by Decky itself. That evidence is anecdotal and secondary. Any Decky plugin carries this risk; it is outside Decky Pilot's control.

## Product rules (binding for future work)

1. **Never** add game memory access, process injection, render hooking, game file modification or input automation, not even for convenience features such as the planned controller shortcut (DP-019), which must not intercept or synthesize game input.
2. **Never** automate Steam (store, friends, chat, trading, account or Web API) or touch Steam client files.
3. **Single-player and non-competitive help is the intended use.** Before any public release, add a competitive-play guard (DP-026): for titles with online PvP or known anti-cheat, show a clear warning and keep automatic visual help unavailable, so the player decides with informed consent. Manual help stays available and is the player's responsibility under that game's rules.
4. Keep acquisition at the compositor level only and keep the existing per-session consent, visible indicator and pause.
5. README and store text must state: Decky Pilot is not a cheat, and it must not be used where a game's rules forbid assistants or outside help.

## Device testing rules

Device runs must not launch games, inject input into the Steam UI, enable CEF remote debugging, touch Steam files or settings, or use the owner's Steam account in any way. The 17 October 2026 run followed these rules (see HARDWARE_VALIDATION).

## Sources

- [Steam Subscriber Agreement](https://store.steampowered.com/subscriber_agreement/) §2.G, §4.A–D, §9.C
- [Steam Support: Valve Anti-Cheat (VAC) System](https://help.steampowered.com/en/faqs/view/571A-97DA-70E9-FF74)
- [Valve Developer Community: VAC](https://developer.valvesoftware.com/wiki/Valve_Anti-Cheat) (false positives from recording software, overlays and drivers)
- [Embark: anti-cheat policy FAQ](https://id.embark.games/the-finals/support/faq/44-anti-cheat-policy-faq) (example of a per-game assistant rule)
- [Steamworks: Proton and anti-cheat on Steam Deck](https://partner.steamgames.com/doc/steamdeck/proton)
- Secondary/anecdotal: [Decky Loader guide](https://www.switchbladegaming.com/steam-deck/decky-loader-guide/), [Decky and online safety](https://pulsegeek.com/articles/decky-loader-and-online-safety-what-to-consider/), [overlay/anti-cheat compatibility notes](https://backgrind.com/overlay-anticheat-checker/)
