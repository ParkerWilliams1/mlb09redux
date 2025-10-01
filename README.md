# MLB 09 Redux

MLB 09 Redux is a project that brings **MLB 09: The Show** (PS2) into the modern era by injecting over **1,200 current MLB players** directly into the game’s save files. 

![screenshot](screen.png)

The project uses **Python**, official **MLB APIs**, and **computer vision** with [DeepFace](https://github.com/serengil/deepface) to generate accurate player attributes, appearances, and rosters.

## Features
- Injects **1,200+ real MLB players** into a MLB 09: The Show (PS2).
- Pulls live player data from the **MLB and MLB The Show APIs**.
- Generates accurate:
  - Names  
  - Positions  
  - Ratings  
  - Height & weight  
  - Skin tone & ethnicity (via DeepFace analysis)
- Fully automated player injection into **game hex save files**.
- Breathing new life into a beloved baseball game.

## Tech Stack
- **Python** – scripting and automation
- **DeepFace** – skin tone & ethnicity classification
- **MLB API & MLB The Show API** – real player data
- **Hex file manipulation** – direct save file editing

## How It Works
1. **Fetch Player Data:**  
   Python scripts query the MLB APIs to retrieve up-to-date player stats and information.

2. **Analyze Player Images:**  
   DeepFace processes player photos to determine **skin tone and ethnicity**, ensuring realistic in-game representations.

3. **Generate Injection Data:**  
   Scripts format player information into the exact byte structure required for MLB 09 save files.

4. **Inject into Game Saves:**  
   Final data is written directly into the game’s hex files, replacing outdated players with the **current 2025 MLB roster**.

## Example Output
Before → After  
- Default 2008 stats → Accurate 2025 ratings and positions  

<!-- ## Demonstration -->
<!-- Check out the project in action: [YouTube Demonstration](https://www.youtube.com) -->
## Future Improvements
- Add support for free agent players.
- Update team textures.
- Build a simple GUI for roster injection.

## License
This project is for **educational purposes only**.  
All MLB player data is property of **Major League Baseball** and **MLB The Show**.
